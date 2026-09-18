import { Play, Printer, RotateCcw, Building2, FileText, Presentation } from "lucide-react";

export const Header = ({ hotel, onPresenter, onPrint, onReset, presenterActive }) => (
  <header className="no-print sticky top-0 z-40 h-16 px-6 flex items-center justify-between border-b border-[#232A3B] bg-[#0B0E14]/90 backdrop-blur-md">
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-[#E2B859]/15 border border-[#E2B859]/40 flex items-center justify-center">
        <Building2 size={18} className="gold-text" />
      </div>
      <div>
        <h1 data-testid="dashboard-header-title" className="font-heading text-lg font-bold tracking-tight leading-none">
          {hotel?.name || "Grand Horizon Palace"} <span className="text-[#64748B] font-medium">· {hotel?.city || "Mumbai"}</span>
        </h1>
        <p className="eyebrow mt-1">AI Dynamic Pricing & Revenue Management Simulator</p>
      </div>
    </div>
    <div className="flex items-center gap-2">
      <span data-testid="currency-indicator" className="font-mono text-xs text-[#94A3B8] px-3 py-1.5 rounded-full border border-[#232A3B]">INR ₹ · {hotel?.total_rooms || 100} rooms</span>
      <button data-testid="reset-scenario-button" onClick={onReset} className="btn-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"><RotateCcw size={13} /> Reset</button>
      <a data-testid="download-documentation-link" href={`${process.env.REACT_APP_BACKEND_URL}/api/docs/documentation`} className="btn-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"><FileText size={13} /> Documentation</a>
      <a data-testid="download-deck-link" href={`${process.env.REACT_APP_BACKEND_URL}/api/docs/deck`} className="btn-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"><Presentation size={13} /> Slide Deck</a>
      <button data-testid="export-pdf-strategy-button" onClick={onPrint} className="btn-ghost text-xs px-3 py-1.5 flex items-center gap-1.5"><Printer size={13} /> Strategy Sheet</button>
      <button data-testid="presenter-mode-toggle-button" onClick={onPresenter} className="btn-gold text-xs px-4 py-1.5 flex items-center gap-1.5">
        <span className={`w-1.5 h-1.5 rounded-full bg-[#0B0E14] ${presenterActive ? "pulse-dot" : ""}`} /> <Play size={13} /> Presenter Mode
      </button>
    </div>
  </header>
);
