from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict
from datetime import datetime, timezone
from pathlib import Path
import os, json, hashlib, logging, re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from engine import HOTEL, PRESETS, SEGMENTS, optimize, simulate, forecast, pace_status, fallback_explanation

client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Hotel Dynamic Pricing Simulator")
api = APIRouter(prefix="/api")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Scenario(BaseModel):
    demand_index: int = Field(100, ge=0, le=200)
    capacity_remaining_pct: int = Field(60, ge=0, le=100)
    days_to_arrival: int = Field(14, ge=1, le=90)
    season: Literal["peak", "shoulder", "off"] = "shoulder"
    competitor_price: int = Field(5200, ge=1000, le=20000)
    event_flag: bool = False
    current_price: int = Field(5000, ge=1000, le=20000)


class SimulateRequest(BaseModel):
    scenario: Scenario
    price: float
    iterations: int = Field(500, ge=100, le=2000)


class ExplainRequest(BaseModel):
    scenario: Scenario
    optimization: Dict[str, Any]
    simulation: Dict[str, Any]
    force: bool = False


class RunCreate(BaseModel):
    label: str = ""
    scenario: Scenario
    optimization: Dict[str, Any]
    simulation: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None
    decision: Literal["accepted", "overridden", "draft"] = "draft"
    override_price: Optional[float] = None


def scenario_key(s: dict, price: float) -> str:
    raw = json.dumps({**s, "price": round(price / 50) * 50}, sort_keys=True)
    return hashlib.sha1(raw.encode()).hexdigest()


@api.get("/")
async def root():
    return {"message": "Hotel Dynamic Pricing Simulator API"}


@api.get("/config")
async def get_config():
    return {"hotel": HOTEL, "segments": SEGMENTS, "presets": PRESETS, "default_scenario": Scenario().model_dump()}


@api.get("/forecast")
async def get_forecast(seed: int = 42):
    return forecast(seed)


@api.post("/pace")
async def get_pace(s: Scenario):
    return pace_status(s.model_dump())


@api.post("/optimize")
async def post_optimize(s: Scenario):
    result = optimize(s.model_dump())
    if result["warnings"]:
        await db.warning_log.insert_one({"scenario": s.model_dump(), "price": result["recommended_price"], "warnings": result["warnings"], "created_at": datetime.now(timezone.utc).isoformat()})
    return result


@api.post("/simulate")
async def post_simulate(req: SimulateRequest):
    return simulate(req.scenario.model_dump(), req.price, req.iterations)


@api.post("/recommend")
async def post_recommend(s: Scenario):
    sd = s.model_dump()
    opt = optimize(sd)
    sim = simulate(sd, opt["recommended_price"])
    sim_current = simulate(sd, sd["current_price"])
    sim_comp = simulate(sd, sd["competitor_price"])
    if opt["warnings"]:
        await db.warning_log.insert_one({"scenario": sd, "price": opt["recommended_price"], "warnings": opt["warnings"], "created_at": datetime.now(timezone.utc).isoformat()})
    return {"scenario": sd, "optimization": opt, "simulation": sim, "simulation_current": sim_current, "simulation_competitor": sim_comp, "pace": pace_status(sd)}


def parse_llm_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    data = json.loads(cleaned[start:end + 1])
    risks = data.get("key_risks", [])
    if isinstance(risks, str):
        risks = [risks]
    return {"why_this_price": str(data.get("why_this_price", "")), "key_risks": [str(r) for r in risks][:4], "alternative_strategy": str(data.get("alternative_strategy", ""))}


async def call_llm(s: dict, opt: dict, sim: dict) -> dict:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise RuntimeError("EMERGENT_LLM_KEY missing")
    chat = LlmChat(
        api_key=key,
        session_id=f"explain-{scenario_key(s, opt['recommended_price'])}",
        system_message=(
            "You are a senior hotel revenue manager explaining a pricing decision to MBA students in plain English. "
            "Be concrete, cite the numbers given, avoid jargon. Respond ONLY with valid JSON with keys: "
            "why_this_price (string, 2-3 sentences), key_risks (array of 3 short strings), alternative_strategy (string, 2 sentences)."
        ),
    ).with_model("gemini", "gemini-3-flash-preview")
    payload = {
        "hotel": {"rooms": HOTEL["total_rooms"], "base_rate_inr": HOTEL["base_rate"], "variable_cost_inr": HOTEL["variable_cost"]},
        "scenario": s,
        "recommended_price_inr": opt["recommended_price"],
        "formula_price_inr": opt["formula_price"],
        "multipliers": opt["multipliers"],
        "expected_at_recommended": opt["expected"],
        "expected_at_current": opt["current"],
        "monte_carlo": {k: sim[k] for k in ("revenue_p10", "revenue_p50", "revenue_p90", "occupancy_final_mean", "conversion_rate", "sellout_probability")},
        "warnings": [w["title"] for w in opt["warnings"]],
    }
    resp = await chat.send_message(UserMessage(text=f"Explain this pricing recommendation:\n{json.dumps(payload)}"))
    return parse_llm_json(resp)


@api.post("/explain")
async def post_explain(req: ExplainRequest):
    sd = req.scenario.model_dump()
    key = scenario_key(sd, req.optimization["recommended_price"])
    if not req.force:
        cached = await db.explanations.find_one({"key": key}, {"_id": 0})
        if cached:
            return {**cached["explanation"], "cached": True}
    try:
        expl = await call_llm(sd, req.optimization, req.simulation)
        expl["source"] = "gemini-3-flash"
    except Exception as e:
        logger.warning(f"LLM explain failed, using fallback: {e}")
        expl = fallback_explanation(sd, req.optimization, req.simulation)
    await db.explanations.update_one({"key": key}, {"$set": {"key": key, "scenario": sd, "explanation": expl, "created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    return {**expl, "cached": False}


@api.post("/runs")
async def create_run(run: RunCreate):
    doc = run.model_dump()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    res = await db.runs.insert_one(doc)
    return {"id": str(res.inserted_id), "created_at": doc["created_at"]}


@api.get("/runs")
async def list_runs(limit: int = 20):
    docs = await db.runs.find({}).sort("created_at", -1).to_list(limit)
    out = []
    for d in docs:
        out.append({
            "id": str(d["_id"]), "label": d.get("label", ""), "decision": d.get("decision"), "created_at": d.get("created_at"),
            "scenario": d.get("scenario"), "recommended_price": d.get("optimization", {}).get("recommended_price"),
            "override_price": d.get("override_price"), "revenue_p50": d.get("simulation", {}).get("revenue_p50"),
            "warnings": len(d.get("optimization", {}).get("warnings", [])),
        })
    return out


@api.get("/warnings/log")
async def warning_log(limit: int = 30):
    docs = await db.warning_log.find({}, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return docs


DOC_PATH = ROOT_DIR / "docs" / "Hotel_Dynamic_Pricing_Simulator_Documentation.docx"
DECK_PATH = ROOT_DIR / "docs" / "Hotel_Dynamic_Pricing_Simulator_Deck.pptx"


@api.get("/docs/documentation")
async def download_documentation():
    if not DOC_PATH.exists():
        raise HTTPException(status_code=404, detail="Documentation not generated")
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(DOC_PATH),
        filename=DOC_PATH.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@api.get("/docs/deck")
async def download_deck():
    if not DECK_PATH.exists():
        raise HTTPException(status_code=404, detail="Deck not generated")
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(DECK_PATH),
        filename=DECK_PATH.name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


app.include_router(api)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','), allow_methods=["*"], allow_headers=["*"])


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
