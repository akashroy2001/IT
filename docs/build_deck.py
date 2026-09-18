"""Builds the 12-slide projection deck (.pptx) for the Hotel Dynamic Pricing Simulator.

Dark Obsidian / Champagne-Gold theme matching the live app. 16:9 widescreen.
Slide 11 is Contributions (8 members mapped to project areas); slide 12 is Thank You.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", "docs")
OUT = os.path.join(OUT_DIR, "Hotel_Dynamic_Pricing_Simulator_Deck.pptx")

# ---------- palette ----------
OBSIDIAN = RGBColor(0x0B, 0x0E, 0x14)
PANEL    = RGBColor(0x12, 0x16, 0x20)
PANEL2   = RGBColor(0x16, 0x1C, 0x28)
GOLD     = RGBColor(0xE2, 0xB8, 0x59)
GOLD_DK  = RGBColor(0x8A, 0x62, 0x00)
TEXT     = RGBColor(0xE5, 0xE7, 0xEB)
MUTED    = RGBColor(0x94, 0xA3, 0xB8)
FAINT    = RGBColor(0x64, 0x74, 0x8B)
BORDER   = RGBColor(0x23, 0x2A, 0x3B)
AMBER    = RGBColor(0xF5, 0xB3, 0x4A)

HEAD = "Calibri Light"
BODY = "Calibri"
MONO = "Consolas"

EMU_W, EMU_H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = EMU_W
prs.slide_height = EMU_H
BLANK = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, EMU_W, EMU_H)
    bg.fill.solid(); bg.fill.fore_color.rgb = OBSIDIAN
    bg.line.fill.background()
    bg.shadow.inherit = False
    # push background to back
    sp = bg._element
    sp.getparent().remove(sp)
    s.shapes._spTree.insert(2, sp)
    return s


def _set_font(run, size, color, bold=False, italic=False, name=BODY):
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = name


def text(s, left, top, width, height, runs, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, space_after=4, line_spacing=1.05):
    """runs: list of paragraphs, each a list of (txt, size, color, bold, italic, name) tuples."""
    tb = s.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.space_before = Pt(0)
        p.line_spacing = line_spacing
        for seg in para:
            txt, size, color = seg[0], seg[1], seg[2]
            bold = seg[3] if len(seg) > 3 else False
            italic = seg[4] if len(seg) > 4 else False
            name = seg[5] if len(seg) > 5 else BODY
            r = p.add_run(); r.text = txt
            _set_font(r, size, color, bold, italic, name)
    return tb


def rect(s, left, top, width, height, fill=PANEL, line=BORDER, line_w=1.0, radius=True):
    shp = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        left, top, width, height)
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    if radius:
        try:
            shp.adjustments[0] = 0.06
        except Exception:
            pass
    return shp


def accent_bar(s, left, top, height=Inches(0.42), width=Inches(0.09)):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bar.fill.solid(); bar.fill.fore_color.rgb = GOLD
    bar.line.fill.background(); bar.shadow.inherit = False
    return bar


def header(s, eyebrow, title, n):
    accent_bar(s, Inches(0.55), Inches(0.5))
    text(s, Inches(0.78), Inches(0.42), Inches(11.4), Inches(0.9), [
        [(eyebrow.upper(), 11, GOLD, True, False, BODY)],
        [(title, 27, TEXT, True, False, HEAD)],
    ], space_after=2)
    # page number chip
    text(s, Inches(12.2), Inches(0.5), Inches(0.9), Inches(0.4),
         [[(f"{n:02d} / 12", 10, FAINT, False, False, MONO)]], align=PP_ALIGN.RIGHT)
    # thin divider
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.78), Inches(1.38), Inches(11.75), Pt(1.4))
    ln.fill.solid(); ln.fill.fore_color.rgb = BORDER; ln.line.fill.background(); ln.shadow.inherit = False


def footer(s):
    text(s, Inches(0.78), Inches(7.02), Inches(11.75), Inches(0.35),
         [[("The Grand Horizon Palace · AI Dynamic Pricing & Revenue Management Simulator",
            8.5, FAINT, False, True, BODY)]])


def card(s, left, top, width, height, title, lines, fill=PANEL, title_color=GOLD,
         icon=None, title_size=13, body_size=10.5):
    rect(s, left, top, width, height, fill=fill)
    inner_l = left + Inches(0.22)
    inner_w = width - Inches(0.44)
    paras = []
    head_txt = (f"{icon}  " if icon else "") + title
    paras.append([(head_txt, title_size, title_color, True, False, BODY)])
    for ln in lines:
        if isinstance(ln, tuple):
            paras.append([(ln[0] + "  ", body_size, TEXT, True, False, BODY),
                          (ln[1], body_size, MUTED, False, False, BODY)])
        else:
            paras.append([(ln, body_size, MUTED, False, False, BODY)])
    text(s, inner_l, top + Inches(0.18), inner_w, height - Inches(0.3), paras, space_after=5,
         line_spacing=1.05)


def formula_box(s, left, top, width, txt, height=Inches(0.55)):
    rect(s, left, top, width, height, fill=PANEL2, line=GOLD_DK, line_w=1.0)
    text(s, left + Inches(0.2), top, width - Inches(0.4), height,
         [[(txt, 11.5, GOLD, True, False, MONO)]], anchor=MSO_ANCHOR.MIDDLE)


def pic(s, filename, left, top, width, caption=None):
    path = os.path.join(IMG, filename)
    if not os.path.exists(path):
        return
    p = s.shapes.add_picture(path, left, top, width=width)
    # gold frame
    fr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, p.left, p.top, p.width, p.height)
    fr.fill.background(); fr.line.color.rgb = BORDER; fr.line.width = Pt(1.0)
    fr.shadow.inherit = False
    if caption:
        text(s, left, top + p.height + Inches(0.04), width, Inches(0.4),
             [[(caption, 8.5, FAINT, False, True, BODY)]], align=PP_ALIGN.CENTER)
    return p


# ============================================================= SLIDE 1 — TITLE
s = slide()
# faint hero image on the right, framed
hero = os.path.join(IMG, "doc_hero.png")
# left accent column
col = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.16), EMU_H)
col.fill.solid(); col.fill.fore_color.rgb = GOLD; col.line.fill.background(); col.shadow.inherit = False

text(s, Inches(0.9), Inches(1.1), Inches(11.5), Inches(0.5),
     [[("MBA (IT & SYSTEMS) · LIVE CLASSROOM DEMONSTRATION · JUNE 2026", 12.5, GOLD, True, False, BODY)]])

text(s, Inches(0.85), Inches(1.9), Inches(11.6), Inches(2.4), [
    [("AI Dynamic Pricing &", 46, TEXT, True, False, HEAD)],
    [("Revenue Management Simulator", 46, TEXT, True, False, HEAD)],
], space_after=2, line_spacing=1.0)

# gold underline
ul = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(3.85), Inches(4.6), Pt(3))
ul.fill.solid(); ul.fill.fore_color.rgb = GOLD; ul.line.fill.background(); ul.shadow.inherit = False

text(s, Inches(0.9), Inches(4.15), Inches(11.4), Inches(1.0), [
    [("Turning revenue-management theory into a decision you can watch happen — ",
      15, MUTED, False, False, BODY)],
    [("pricing mathematics, a simulated customer market, and an AI that explains every call.",
      15, MUTED, False, False, BODY)],
], line_spacing=1.15)

# case card
rect(s, Inches(0.9), Inches(5.55), Inches(11.5), Inches(1.1), fill=PANEL)
text(s, Inches(1.15), Inches(5.62), Inches(11.0), Inches(1.0), [
    [("CASE SETTING", 10, GOLD, True, False, BODY)],
    [("The Grand Horizon Palace, Mumbai", 16, TEXT, True, False, HEAD),
     ("   ·  100 rooms · single room type · base rate ₹5,000 · currency INR",
      13, MUTED, False, False, BODY)],
], space_after=3)

# ============================================================= SLIDE 2 — PROBLEM
s = slide()
header(s, "The problem", "Why hotel pricing is hard", 2)
text(s, Inches(0.78), Inches(1.55), Inches(11.75), Inches(0.7),
     [[("A hotel room is perishable inventory on fixed capacity: tonight's unsold room is worth ",
        12.5, MUTED, False, False, BODY),
       ("₹0 at midnight", 12.5, GOLD, True, False, BODY),
       (", yet the hotel cannot add a floor because a concert came to town. That tension is revenue management.",
        12.5, MUTED, False, False, BODY)]], line_spacing=1.1)

cw, ch, gap = Inches(2.83), Inches(2.2), Inches(0.13)
x0, y0 = Inches(0.78), Inches(2.5)
cards = [
    ("Demand uncertainty", ["Only a forecast with a band around it. Pricing for the average empties the hotel in bad weeks."]),
    ("Time pressure", ["Willingness to pay shifts as arrival nears — leisure books early on price, business books late on availability."]),
    ("Competitor pressure", ["Rates are public. A rival can cut 40% overnight and reshape the conversion curve instantly."]),
    ("Cost & reputation floors", ["Below variable cost every sale loses money; far above the market, the brand takes the damage."]),
]
for i, (t, ls) in enumerate(cards):
    card(s, x0 + i * (cw + gap), y0, cw, ch, t, ls, title_size=13, body_size=10.5)

formula_box(s, Inches(0.78), Inches(5.15), Inches(11.75),
            "RevPAR = Occupancy × ADR      Expected revenue = Price × Expected bookings at that price")
text(s, Inches(0.78), Inches(5.9), Inches(11.75), Inches(0.9),
     [[("Because bookings fall as price rises, expected revenue is ", 12.5, MUTED, False, False, BODY),
       ("a curve with a peak, not a line", 12.5, GOLD, True, False, BODY),
       (". The simulator makes that peak visible — and shows how far it moves when one condition changes.",
        12.5, MUTED, False, False, BODY)]], line_spacing=1.1)
footer(s)

# ============================================================= SLIDE 3 — FOUR ZONES
s = slide()
header(s, "Solution overview", "One screen, four zones", 3)
text(s, Inches(0.78), Inches(1.55), Inches(11.75), Inches(0.5),
     [[("A single dashboard so the presenter never navigates away from the decision — three visible zones plus a compliance view.",
        12.5, MUTED, False, False, BODY)]])
zw, zh, zg = Inches(5.78), Inches(1.9), Inches(0.19)
zx, zy = Inches(0.78), Inches(2.35)
zones = [
    ("ZONE 1 — Manager panel", GOLD, ["Five sliders, season selector, event switch and four one-click shock presets. Sets up the night, or fires a preset to change the world instantly."]),
    ("ZONE 2 — Recommendation & analytics", GOLD, ["Recommended rate, multiplier chain, 14-day forecast, booking pace, the Monte Carlo distribution and the comparison table."]),
    ("ZONE 3 — Guardrails & AI", GOLD, ["Ethical/policy flags plus the Gemini 3 Flash rationale that streams in word by word — the model can be challenged live."]),
    ("ZONE 4 — Warning audit log", GOLD, ["A timestamped server-side record of every flag ever raised. Answers: can you prove what the system flagged, and when?"]),
]
for i, (t, c, ls) in enumerate(zones):
    r, col_i = divmod(i, 2)
    card(s, zx + col_i * (zw + zg), zy + r * (zh + zg), zw, zh, t, ls, title_color=c, title_size=13, body_size=11)

formula_box(s, Inches(0.78), Inches(6.35), Inches(11.75),
            "Set scenario  →  optimize  →  simulate ×500  →  evaluate guardrails  →  AI explains  →  accept / override & save",
            height=Inches(0.5))
footer(s)

# ============================================================= SLIDE 4 — DECISION
s = slide()
header(s, "The engine", "How the price is decided — no black box", 4)
formula_box(s, Inches(0.78), Inches(1.6), Inches(11.75),
            "Formula price = BaseRate × Season × Demand × Scarcity × Competitor × LeadTime × Event")
cw, ch, gap = Inches(3.82), Inches(2.35), Inches(0.14)
x0, y0 = Inches(0.78), Inches(2.4)
card(s, x0, y0, cw, ch, "1 · Multiplier chain",
     [("Base ₹5,000", "adjusted by seven independent factors, each answering one business question."),
      ("Demand damped:", "only 40% of the movement passes to price, capped at 1.40."),
      ("Scarcity convex:", "the last rooms move the rate sharply, the first barely at all.")], body_size=10)
card(s, x0 + (cw + gap), y0, cw, ch, "2 · Revenue-max search",
     [("Grid ±30%", "around the formula price in ₹50 steps."),
      ("argmax", "Price × expected bookings — the money-maximising rate, not the highest legal one."),
      ("Constraint:", "must fill ≥75% of remaining rooms.")], body_size=10)
card(s, x0 + 2 * (cw + gap), y0, cw, ch, "3 · Hard rules",
     [("Floor / ceiling:", "0.2× to 3.0× base (₹1,000–₹15,000)."),
      ("Cost floor:", "₹1,200 variable cost per occupied room."),
      ("Below that", "raises a warning — an empty room becomes a loss-making one.")], body_size=10)
formula_box(s, Inches(0.78), Inches(5.05), Inches(11.75),
            "Recommended price = argmax over candidates ( Price × Expected bookings at that price )")
text(s, Inches(0.78), Inches(5.8), Inches(11.75), Inches(0.9),
     [[("The key idea: ", 12.5, GOLD, True, False, BODY),
       ("the recommendation is where the rate-vs-volume trade-off makes the most money. Raising further is rejected by the optimizer itself — not by a policy.",
        12.5, MUTED, False, False, BODY)]], line_spacing=1.1)
footer(s)

# ============================================================= SLIDE 5 — WORKED EXAMPLE
s = slide()
header(s, "Worked example", "\u201cConcert in Town\u201d — reproducible live", 5)
# left: inputs + chain
card(s, Inches(0.78), Inches(1.6), Inches(6.1), Inches(2.35), "Scenario",
     [("Demand 175", "market 75% hotter than normal"),
      ("35 rooms left", "two-thirds already sold · 5 days out"),
      ("Competitor ₹8,200", "market already repriced · event on")], body_size=11)
formula_box(s, Inches(0.78), Inches(4.15), Inches(6.1),
            "₹5,000 ×1.00 ×1.30 ×1.211 ×1.192 ×1.08 ×1.20", height=Inches(0.55))
text(s, Inches(0.78), Inches(4.8), Inches(6.1), Inches(0.9),
     [[("Formula price ₹12,160", 13, TEXT, True, False, BODY),
       ("  →  ", 13, MUTED, False, False, BODY),
       ("recommended ₹12,412", 15, GOLD, True, False, BODY)],
      [("with only 35 rooms left, the hotel still sells out at the higher rate.", 10.5, MUTED, False, True, BODY)]],
     space_after=3)

# right: comparison mini table
rect(s, Inches(7.1), Inches(1.6), Inches(5.43), Inches(4.15), fill=PANEL)
text(s, Inches(7.32), Inches(1.72), Inches(5.0), Inches(0.4),
     [[("WHY THE HIGHER RATE WINS", 11, GOLD, True, False, BODY)]])
rows = [
    ("", "Current ₹5,000", "Rec ₹12,412"),
    ("Leisure conversion", "93.3%", "31.4%"),
    ("Business conversion", "87.9%", "52.4%"),
    ("Expected bookings", "35.0", "35.0"),
    ("Expected revenue", "₹1.75 L", "₹4.34 L"),
]
ry = Inches(2.2)
for i, (a, b, c) in enumerate(rows):
    is_head = i == 0
    col_a = GOLD if is_head else MUTED
    col_bc = GOLD if is_head else TEXT
    text(s, Inches(7.32), ry, Inches(2.5), Inches(0.4),
         [[(a, 11, col_a, is_head, False, BODY)]])
    text(s, Inches(9.75), ry, Inches(1.35), Inches(0.4),
         [[(b, 11, col_bc, is_head, False, MONO if not is_head else BODY)]], align=PP_ALIGN.RIGHT)
    text(s, Inches(11.15), ry, Inches(1.25), Inches(0.4),
         [[(c, 11, GOLD if i == 4 else col_bc, is_head or i == 4, False, MONO if not is_head else BODY)]], align=PP_ALIGN.RIGHT)
    if i == 0:
        ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.32), ry + Inches(0.35), Inches(4.9), Pt(1))
        ln.fill.solid(); ln.fill.fore_color.rgb = BORDER; ln.line.fill.background(); ln.shadow.inherit = False
    ry += Inches(0.62)
text(s, Inches(7.32), Inches(5.25), Inches(5.0), Inches(0.5),
     [[("Teaching point: ", 10.5, GOLD, True, False, BODY),
       ("conversion collapses, yet only 35 bookings are needed — so the rate rise is correct.", 10.5, MUTED, False, True, BODY)]],
     line_spacing=1.05)
footer(s)

# ============================================================= SLIDE 6 — CUSTOMER MODEL
s = slide()
header(s, "The market", "How customers are modelled", 6)
text(s, Inches(0.78), Inches(1.55), Inches(11.75), Inches(0.45),
     [[("Two segments, because one \u201caverage guest\u201d hides the most interesting behaviour in hotel pricing.",
        12.5, MUTED, False, False, BODY)]])
card(s, Inches(0.78), Inches(2.25), Inches(5.78), Inches(1.85), "Leisure · 60% of demand",
     [("Sensitivity k ≈ 4.5", "a cliff — a 20% premium destroys most bookings"),
      ("Books early", "compares hotels, walks when the rate beats the market reference")], body_size=11)
card(s, Inches(6.75), Inches(2.25), Inches(5.78), Inches(1.85), "Business · 40% of demand",
     [("Sensitivity k ≈ 1.8", "a slope — the same premium costs few bookings"),
      ("Books late", "needs a room on a date; hardens to k≈1.2 inside three days")], body_size=11)
formula_box(s, Inches(0.78), Inches(4.35), Inches(11.75),
            "Conversion(P) = 2·Baseline ÷ ( 1 + exp( k·(P÷Reference − 1) ) )     bounded 2%–95%")
formula_box(s, Inches(0.78), Inches(5.05), Inches(11.75),
            "Reference = (0.5·Competitor + 0.5·Base) × 1.15 × SeasonDemand × Event × Scarcity × Urgency")
text(s, Inches(0.78), Inches(5.85), Inches(11.75), Inches(0.9),
     [[("The single parameter ", 12.5, MUTED, False, False, BODY),
       ("k", 12.5, GOLD, True, False, MONO),
       (" is what makes business demand profitable to price into and leisure demand dangerous to price into.",
        12.5, MUTED, False, False, BODY)]], line_spacing=1.1)
footer(s)

# ============================================================= SLIDE 7 — MONTE CARLO
s = slide()
header(s, "Confidence", "The Monte Carlo simulation — 500 runs", 7)
text(s, Inches(0.78), Inches(1.55), Inches(6.4), Inches(0.6),
     [[("One revenue number implies a certainty that does not exist. So the night is run 500 times with random variation.",
        12, MUTED, False, False, BODY)]], line_spacing=1.1)
card(s, Inches(0.78), Inches(2.35), Inches(6.4), Inches(2.05), "What varies each run",
     [("Demand volume", "Poisson arrivals × log-normal noise"),
      ("Conversion", "perturbed ±12% around the curve"),
      ("Booking outcome", "each guest a binomial book / no-book"),
      ("Capacity", "capped at rooms actually available")], body_size=10.5)
card(s, Inches(0.78), Inches(4.55), Inches(6.4), Inches(2.0), "Reading the output (worked example)",
     [("P10 / P50 / P90", "₹3.10 L · ₹4.34 L · ₹4.34 L"),
      ("P10=P90", "signature of a capacity-constrained, sell-out night"),
      ("Sell-out probability 51%", "the honest answer to \u201cwill this work?\u201d")], body_size=10.5)
pic(s, "doc_montecarlo.png", Inches(7.45), Inches(1.7), Inches(5.1),
    "500-run revenue distribution with P10 / P50 / P90 markers")
footer(s)

# ============================================================= SLIDE 8 — FORECAST & PACE
s = slide()
header(s, "Timing", "Forecasting & booking pace", 8)
card(s, Inches(0.78), Inches(1.6), Inches(6.1), Inches(2.1), "14-day demand forecast",
     [("Seasonal wave × day-of-week + noise", "365 seeded days projected forward"),
      ("The band widens ~1.2 pts/day out", "a forecast is a cone, not a line — decisions 14 days out deserve less conviction")], body_size=11)
card(s, Inches(0.78), Inches(3.85), Inches(6.1), Inches(2.7), "Booking pace · pickup model",
     [("Expected share = 100·e^(−Days÷12)", ""),
      ("Pace index = Actual ÷ Expected", ""),
      ("> 1.1  ahead of pace", "sell faster — hold or push the rate"),
      ("~ 1.0  on the books", "the rate is roughly right"),
      ("< 0.9  behind pace", "cut the rate or add promotion")], body_size=10.5)
pic(s, "doc_charts.png", Inches(7.2), Inches(2.2), Inches(5.35),
    "14-day forecast cone (left) and the pickup pace curve (right)")
footer(s)

# ============================================================= SLIDE 9 — GUARDRAILS
s = slide()
header(s, "Responsibility", "Ethical & policy guardrails", 9)
gw, gh, gg = Inches(2.83), Inches(2.0), Inches(0.13)
gx, gy = Inches(0.78), Inches(1.6)
flags = [
    ("SURGE", "Rate > 2.5× base", "Cap at 2.5× or add value to justify the premium"),
    ("BELOW COST", "Rate < ₹1,200 cost", "Hold at the cost floor, accept lower occupancy"),
    ("FAIRNESS", "Segment rates differ >50%", "Use fenced rates, not segment-based pricing"),
    ("PARITY", "Rate > 40% over competitor", "Monitor pickup, step down in ₹250 increments"),
]
for i, (fl, trig, mit) in enumerate(flags):
    rect(s, gx + i * (gw + gg), gy, gw, gh, fill=PANEL)
    text(s, gx + i * (gw + gg) + Inches(0.2), gy + Inches(0.16), gw - Inches(0.4), gh - Inches(0.3), [
        [(fl, 14, AMBER, True, False, BODY)],
        [(trig, 10.5, TEXT, True, False, BODY)],
        [("→ " + mit, 10, MUTED, False, False, BODY)],
    ], space_after=6, line_spacing=1.05)
rect(s, Inches(0.78), Inches(3.85), Inches(6.1), Inches(2.55), fill=PANEL2, line=GOLD_DK)
text(s, Inches(1.0), Inches(4.0), Inches(5.7), Inches(2.3), [
    [("Flag, do not block", 15, GOLD, True, False, HEAD)],
    [("The system never refuses to show a price. It shows the price, shows the flag, and leaves the call to a named human.",
      11, MUTED, False, False, BODY)],
    [("• A hard block hides the trade-off the manager needs to see.", 10.5, TEXT, False, False, BODY)],
    [("• Accountability requires a decision-maker, not an algorithm.", 10.5, TEXT, False, False, BODY)],
], space_after=6, line_spacing=1.08)
card(s, Inches(7.1), Inches(3.85), Inches(5.43), Inches(2.55), "The audit log = the compliance answer",
     [("Every flag is written to the database", "with the rate, full scenario and a timestamp."),
      ("Replayed newest-first", "with running totals — \u201cwhat did you warn me about, and when?\u201d has a documented answer."),
      ("Screen-only", "deliberately excluded from the printable strategy sheet.")], body_size=10.5)
footer(s)

# ============================================================= SLIDE 10 — AI + PRESENTER
s = slide()
header(s, "Explanation & delivery", "The AI layer + Presenter Mode", 10)
card(s, Inches(0.78), Inches(1.6), Inches(6.1), Inches(2.5), "Gemini 3 Flash explains the number",
     [("Sent:", "a compact numerical brief — scenario, recommendation, multipliers, Monte Carlo summary, flags. No free text, no guest data."),
      ("Returns:", "Why this price · three specific risks · an alternative strategy — as a senior RM would brief the room.")], body_size=10.5)
card(s, Inches(0.78), Inches(4.25), Inches(6.1), Inches(2.3), "Three decisions that matter live",
     [("Caching", "same scenario returns instantly, no re-spend"),
      ("Streaming reveal", "word-by-word so the room reads at your pace"),
      ("Deterministic fallback", "the panel is never blank if the network drops")], body_size=10.5)
card(s, Inches(7.1), Inches(1.6), Inches(5.43), Inches(2.5), "Presenter Mode",
     [("Three shock scenarios", "20-second auto-advance, pause & manual step, scripted narration"),
      ("Concert · Competitor −40% · Off-season", "each with its own teaching point"),
      ("Zone spotlight", "dims every panel except the one being discussed")], body_size=10.5)
pic(s, "doc_presenter_price.jpeg", Inches(7.1), Inches(4.25), Inches(5.43),
    "Presenter Mode: the recommendation spotlighted, the rest dimmed")
footer(s)

# ============================================================= SLIDE 11 — CONTRIBUTIONS
s = slide()
header(s, "The team", "Contributions", 11)
text(s, Inches(0.78), Inches(1.5), Inches(11.75), Inches(0.4),
     [[("Eight members, one system — each owning a real part of the build.", 12.5, MUTED, False, False, BODY)]])
members = [
    ("Member 1", "Pricing Optimizer & Multiplier Chain", "Seven-factor chain + bounded revenue-max search"),
    ("Member 2", "Customer Demand Model", "Two-segment logistic price-response & reference price"),
    ("Member 3", "Monte Carlo Simulation Engine", "500-run Poisson × binomial revenue distribution"),
    ("Member 4", "Forecasting & Booking Pace", "14-day seeded forecast cone + pickup pace index"),
    ("Member 5", "Ethical Guardrails & Audit Log", "Surge / cost / fairness / parity flags + compliance trail"),
    ("Member 6", "AI Explanation Layer", "Gemini 3 Flash brief, caching, streaming & fallback"),
    ("Member 7", "Frontend, UI & Presenter Mode", "React dashboard, zone spotlight, strategy sheet"),
    ("Member 8", "Documentation & Project Report", "Word report, this deck & the demo script"),
]
mw, mh, mgx, mgy = Inches(5.78), Inches(1.13), Inches(0.19), Inches(0.14)
mx, my = Inches(0.78), Inches(2.05)
for i, (nm, area, desc) in enumerate(members):
    r, cix = divmod(i, 2)
    lft = mx + cix * (mw + mgx)
    tp = my + r * (mh + mgy)
    rect(s, lft, tp, mw, mh, fill=PANEL)
    # number badge
    badge = s.shapes.add_shape(MSO_SHAPE.OVAL, lft + Inches(0.18), tp + Inches(0.28), Inches(0.55), Inches(0.55))
    badge.fill.solid(); badge.fill.fore_color.rgb = OBSIDIAN
    badge.line.color.rgb = GOLD; badge.line.width = Pt(1.25); badge.shadow.inherit = False
    btf = badge.text_frame; btf.word_wrap = False
    bp = btf.paragraphs[0]; bp.alignment = PP_ALIGN.CENTER
    br = bp.add_run(); br.text = str(i + 1); _set_font(br, 15, GOLD, True, False, HEAD)
    text(s, lft + Inches(0.9), tp + Inches(0.13), mw - Inches(1.05), mh - Inches(0.2), [
        [(nm, 10, GOLD, True, False, BODY)],
        [(area, 12.5, TEXT, True, False, BODY)],
        [(desc, 9.5, MUTED, False, False, BODY)],
    ], space_after=1, line_spacing=1.0)
footer(s)

# ============================================================= SLIDE 12 — THANK YOU
s = slide()
col = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.16), EMU_H)
col.fill.solid(); col.fill.fore_color.rgb = GOLD; col.line.fill.background(); col.shadow.inherit = False
text(s, Inches(0.9), Inches(2.4), Inches(11.5), Inches(0.5),
     [[("MBA (IT & SYSTEMS) · REVENUE MANAGEMENT", 13, GOLD, True, False, BODY)]])
text(s, Inches(0.85), Inches(2.95), Inches(11.6), Inches(1.5),
     [[("Thank you.", 60, TEXT, True, False, HEAD)]])
ul = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(4.35), Inches(3.4), Pt(3))
ul.fill.solid(); ul.fill.fore_color.rgb = GOLD; ul.line.fill.background(); ul.shadow.inherit = False
text(s, Inches(0.9), Inches(4.65), Inches(11.4), Inches(1.0),
     [[("Questions, challenges and \u201cwhat if we changed this slider?\u201d are the point.",
        16, MUTED, False, True, BODY)],
      [("The Grand Horizon Palace, Mumbai · AI Dynamic Pricing & Revenue Management Simulator",
        12, FAINT, False, False, BODY)]], space_after=8)

os.makedirs(OUT_DIR, exist_ok=True)
prs.save(OUT)
print("written", OUT, os.path.getsize(OUT))
