import React, { useState, useEffect, useCallback } from "react";
import "./App.css";

const API = "http://localhost:8000/api";

// ─── Palette ────────────────────────────────────────────────
const BAND_STYLE = {
  "Low Risk":      { bg: "#d1fae5", text: "#065f46", border: "#34d399" },
  "Moderate-Low":  { bg: "#fef9c3", text: "#713f12", border: "#facc15" },
  "Moderate-High": { bg: "#ffedd5", text: "#7c2d12", border: "#fb923c" },
  "High Risk":     { bg: "#fee2e2", text: "#7f1d1d", border: "#f87171" },
};

// ─── Helpers ────────────────────────────────────────────────
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

function GaugeArc({ score }) {
  // score 0–1000
  const pct    = clamp(score / 1000, 0, 1);
  const angle  = -135 + pct * 270; // sweeps 270°
  const R = 80, cx = 100, cy = 105;
  const toXY = (deg) => {
    const r = (deg * Math.PI) / 180;
    return [cx + R * Math.cos(r), cy + R * Math.sin(r)];
  };
  // Arc background segments
  const segments = [
    { from: -135, to: -60,  color: "#34d399" },
    { from: -60,  to:  15,  color: "#facc15" },
    { from:  15,  to:  90,  color: "#fb923c" },
    { from:  90,  to: 135,  color: "#f87171" },
  ];
  const describeArc = (startDeg, endDeg, r) => {
    const [sx, sy] = toXY(startDeg);
    const [ex, ey] = toXY(endDeg);
    const large    = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${sx} ${sy} A ${r} ${r} 0 ${large} 1 ${ex} ${ey}`;
  };
  const [nx, ny] = toXY(angle);
  return (
    <svg viewBox="0 0 200 130" className="gauge-svg">
      {segments.map((s, i) => (
        <path key={i} d={describeArc(s.from, s.to, R)}
          stroke={s.color} strokeWidth="14" fill="none"
          strokeLinecap="round" opacity="0.35" />
      ))}
      <path d={describeArc(-135, angle, R)}
        stroke={pct < 0.15 ? "#34d399" : pct < 0.4 ? "#facc15" : pct < 0.7 ? "#fb923c" : "#f87171"}
        strokeWidth="14" fill="none" strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={nx} y2={ny}
        stroke="#1e293b" strokeWidth="3" strokeLinecap="round" />
      <circle cx={cx} cy={cy} r="5" fill="#1e293b" />
      <text x={cx} y={cy - 18} textAnchor="middle"
        fontSize="22" fontWeight="700" fill="#1e293b">{score}</text>
    </svg>
  );
}

function ShapBar({ feature, shap, direction, abs: absVal, maxAbs }) {
  const barW = clamp((absVal / (maxAbs || 1)) * 100, 2, 100);
  const isRisk = direction === "risk";
  return (
    <div className="shap-row">
      <span className="shap-label">{feature}</span>
      <div className="shap-track">
        <div
          className="shap-fill"
          style={{
            width: `${barW}%`,
            background: isRisk ? "#ef4444" : "#3b82f6",
          }}
        />
      </div>
      <span className="shap-val" style={{ color: isRisk ? "#ef4444" : "#3b82f6" }}>
        {isRisk ? "+" : ""}{shap.toFixed(3)}
      </span>
    </div>
  );
}

// ─── Pages ──────────────────────────────────────────────────

function SingleApplication({ appIdx, setAppIdx, maxIdx }) {
  const [data, setData]     = useState(null);
  const [loading, setLoad]  = useState(false);
  const [feedback, setFb]   = useState("");

  const fetch_ = useCallback(async () => {
    setLoad(true); setData(null); setFb("");
    try {
      const r = await fetch(`${API}/score/${appIdx}`);
      setData(await r.json());
    } finally { setLoad(false); }
  }, [appIdx]);

  useEffect(() => { fetch_(); }, [fetch_]);

  const decide = async (action) => {
    await fetch(`${API}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ app_idx: appIdx, action, reason: "UI action", underwriter: "UW001" }),
    });
    setFb(`✓ ${action} recorded`);
  };

  const band = data ? BAND_STYLE[data.risk_band] || BAND_STYLE["Moderate-High"] : null;
  const maxAbs = data?.shap?.top_reasons?.length
    ? Math.max(...data.shap.top_reasons.map(r => r.abs))
    : 1;

  return (
    <div className="page">
      <div className="page-header">
        <h2>Risk Scoring</h2>
        <div className="app-nav">
          <button onClick={() => setAppIdx(i => Math.max(0, i - 1))} disabled={appIdx === 0}>‹</button>
          <span>Application #{appIdx.toString().padStart(5, "0")}</span>
          <button onClick={() => setAppIdx(i => Math.min(maxIdx, i + 1))} disabled={appIdx === maxIdx}>›</button>
        </div>
      </div>

      {loading && <div className="loading-bar"><div /></div>}

      {data && (
        <>
          {/* Top KPIs */}
          <div className="kpi-row">
            <div className="kpi-card">
              <span className="kpi-label">Risk probability</span>
              <span className="kpi-value" style={{
                color: data.risk_probability > 70 ? "#ef4444"
                     : data.risk_probability > 40 ? "#f97316"
                     : data.risk_probability > 15 ? "#eab308" : "#22c55e"
              }}>{data.risk_probability}%</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-label">Risk band</span>
              <span className="kpi-badge" style={{ background: band.bg, color: band.text, border: `1px solid ${band.border}` }}>
                {data.risk_band}
              </span>
            </div>
            <div className="kpi-card">
              <span className="kpi-label">Recommended action</span>
              <span className="kpi-sub">{data.recommended_action}</span>
            </div>
            <div className="kpi-card">
              <span className="kpi-label">SLA</span>
              <span className="kpi-sub kpi-mono">{data.sla}</span>
            </div>
          </div>

          {/* Gauge + SHAP */}
          <div className="two-col">
            <div className="card">
              <p className="card-label">RISK GAUGE</p>
              <GaugeArc score={data.risk_score_gauge} />
              <p className="ci-text">95% CI: [{data.confidence_lower}%, {data.confidence_upper}%]</p>
              <div className="meta-rows">
                <div className="meta-row"><span>Automation</span><span>{data.automation_level}</span></div>
                <div className="meta-row"><span>Escalation</span><span>{data.escalation_path}</span></div>
                <div className="meta-row"><span>Est. Premium</span><span>{data.portfolio_impact}</span></div>
              </div>
            </div>

            <div className="card">
              <p className="card-label">TOP SHAP RISK DRIVERS</p>
              {data.shap?.top_reasons?.length > 0 ? (
                <>
                  {data.shap.top_reasons.map((r, i) => (
                    <ShapBar key={i} {...r} maxAbs={maxAbs} />
                  ))}
                  <div className="shap-legend">
                    <span><span className="dot" style={{ background: "#ef4444" }} />Increases risk</span>
                    <span><span className="dot" style={{ background: "#3b82f6" }} />Protective</span>
                  </div>
                </>
              ) : (
                <p className="err-msg">{data.shap?.error || "SHAP unavailable"}</p>
              )}
            </div>
          </div>

          {/* Decision buttons */}
          <div className="card">
            <p className="card-label">UNDERWRITER DECISION</p>
            <div className="decision-row">
              <button className="btn-approve"  onClick={() => decide("APPROVE")}>Approve</button>
              <button className="btn-neutral"  onClick={() => decide("REQUEST_INFO")}>Request info</button>
              <button className="btn-decline"  onClick={() => decide("DECLINE")}>Decline</button>
              <button className="btn-escalate" onClick={() => decide("ESCALATE")}>Escalate</button>
            </div>
            {feedback && <p className="feedback-msg">{feedback}</p>}
          </div>
        </>
      )}
    </div>
  );
}

function WhatIfSimulator({ appIdx }) {
  const [orig, setOrig]     = useState(null);
  const [result, setResult] = useState(null);
  const [params, setParams] = useState({
    vehicle_age: 5, power_to_weight: 0.3,
    region_density: 10000, subscription_length: 12,
    ncap_rating: 3, customer_age: 35,
  });

  useEffect(() => {
    fetch(`${API}/score/${appIdx}`)
      .then(r => r.json()).then(d => {
        setOrig(d);
        setResult(null);
      });
  }, [appIdx]);

  const run = async () => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => q.set(k, v));
    const r = await fetch(`${API}/whatif/${appIdx}?${q}`);
    setResult(await r.json());
  };

  const Slider = ({ k, label, min, max, step = 1 }) => (
    <div className="slider-row">
      <label>{label}<span>{params[k]}</span></label>
      <input type="range" min={min} max={max} step={step} value={params[k]}
        onChange={e => setParams(p => ({ ...p, [k]: parseFloat(e.target.value) }))} />
    </div>
  );

  return (
    <div className="page">
      <div className="page-header"><h2>What-If Simulator</h2></div>
      <div className="two-col">
        <div className="card">
          <p className="card-label">ADJUST PARAMETERS</p>
          <Slider k="vehicle_age"        label="Vehicle Age (yrs)"    min={0}    max={20} />
          <Slider k="customer_age"       label="Customer Age"         min={18}   max={80} />
          <Slider k="subscription_length" label="Subscription (months)" min={1}  max={36} />
          <Slider k="region_density"     label="Region Density"       min={1000} max={50000} step={500} />
          <Slider k="power_to_weight"    label="Power-to-Weight"      min={0.05} max={0.8} step={0.01} />
          <Slider k="ncap_rating"        label="NCAP Rating"          min={0}    max={5} step={0.5} />
          <button className="btn-approve" style={{ marginTop: 16 }} onClick={run}>Run Simulation</button>
        </div>

        <div className="card">
          <p className="card-label">COMPARISON</p>
          {orig && (
            <div className="compare-grid">
              <div className="compare-col">
                <p className="compare-head">Original</p>
                <p className="compare-prob" style={{ color: "#64748b" }}>{orig.risk_probability}%</p>
                <p className="compare-band">{orig.risk_band}</p>
              </div>
              {result && (
                <>
                  <div className="compare-arrow">
                    <span style={{ color: result.delta > 0 ? "#ef4444" : "#22c55e", fontSize: 28 }}>
                      {result.delta > 0 ? "▲" : "▼"}
                    </span>
                    <span style={{ color: result.delta > 0 ? "#ef4444" : "#22c55e" }}>
                      {result.delta > 0 ? "+" : ""}{result.delta}%
                    </span>
                  </div>
                  <div className="compare-col">
                    <p className="compare-head">Simulated</p>
                    <p className="compare-prob" style={{
                      color: result.new_probability > 70 ? "#ef4444"
                           : result.new_probability > 40 ? "#f97316" : "#22c55e"
                    }}>{result.new_probability}%</p>
                    <p className="compare-band">{result.risk_band}</p>
                  </div>
                </>
              )}
            </div>
          )}
          {result && (
            <div className="info-box">
              <strong>Recommendation:</strong> {result.recommended_action}<br />
              <strong>SLA:</strong> {result.sla}
            </div>
          )}
          {!result && <p style={{ color: "#94a3b8", marginTop: 24 }}>Adjust sliders and click Run Simulation</p>}
        </div>
      </div>
    </div>
  );
}

function FairnessAudit() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch(`${API}/fairness`).then(r => r.json()).then(setData);
  }, []);

  return (
    <div className="page">
      <div className="page-header"><h2>Fairness Audit</h2></div>
      {data ? (
        <div className="card">
          <p className="card-label">DEMOGRAPHIC PARITY & EQUALIZED ODDS BY REGION</p>
          <div className="table-wrap">
            <table className="rg-table">
              <thead>
                <tr>
                  <th>Group</th><th>N</th><th>Approval Rate</th>
                  <th>TPR</th><th>FPR</th><th>Parity Ratio</th><th>EO Gap</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, i) => (
                  <tr key={i}>
                    <td><strong>{row.group}</strong></td>
                    <td>{row.n.toLocaleString()}</td>
                    <td>{(row.approval_rate * 100).toFixed(1)}%</td>
                    <td>{(row.tpr * 100).toFixed(1)}%</td>
                    <td>{(row.fpr * 100).toFixed(1)}%</td>
                    <td style={{ color: row.parity_ratio < 0.8 ? "#ef4444" : "#22c55e" }}>
                      {row.parity_ratio.toFixed(3)}
                    </td>
                    <td style={{ color: Math.abs(row.equalized_odds_gap) > 0.05 ? "#f97316" : "#22c55e" }}>
                      {row.equalized_odds_gap > 0 ? "+" : ""}{row.equalized_odds_gap.toFixed(3)}
                    </td>
                    <td>
                      <span className="kpi-badge" style={
                        row.parity_ratio < 0.8
                          ? { background: "#fee2e2", color: "#7f1d1d", border: "1px solid #f87171" }
                          : { background: "#d1fae5", color: "#065f46", border: "1px solid #34d399" }
                      }>
                        {row.parity_ratio < 0.8 ? "⚠ Review" : "✓ Pass"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="fine-print">
            Target: parity ratio ≥ 0.80 across all groups (GDPR Art.22 / insurance fairness guidelines).
            EO Gap target: |gap| &lt; 0.05.
          </p>
        </div>
      ) : <div className="loading-spinner">Loading fairness data…</div>}
    </div>
  );
}

function ExecutiveReport() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch(`${API}/report`).then(r => r.json()).then(setData);
  }, []);

  if (!data) return <div className="page"><div className="loading-spinner">Generating report…</div></div>;

  const { metrics, financial } = data;
  const kpis = [
    { label: "AUC-ROC",           value: metrics.auc_roc,  fmt: v => v.toFixed(4), good: v => v > 0.80 },
    { label: "Avg Precision",      value: metrics.avg_prec, fmt: v => v.toFixed(4), good: v => v > 0.70 },
    { label: "Brier Score",        value: metrics.brier,    fmt: v => v.toFixed(4), good: v => v < 0.20 },
    { label: "Opt. Threshold",     value: metrics.opt_threshold, fmt: v => v.toFixed(3), good: () => true },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h2>Executive Risk Assessment Report</h2>
        <span className="kpi-badge" style={{ background: "#f1f5f9", color: "#475569", border: "1px solid #cbd5e1" }}>
          {data.generated}
        </span>
      </div>

      <div className="exec-section">
        <h3>Executive Summary</h3>
        <p className="exec-para">
          RiskGuard's AI underwriting model achieved an AUC-ROC of <strong>{metrics.auc_roc.toFixed(3)}</strong> on the
          holdout test set, with an average precision of {metrics.avg_prec.toFixed(3)} and Brier score of {metrics.brier.toFixed(4)}.
          The model correctly identified <strong>{metrics.tp.toLocaleString()}</strong> true high-risk applications and avoided an
          estimated <strong>${financial.avoided_exposure.toLocaleString()}</strong> in potential claims exposure.
          With optimized thresholds derived from the business cost matrix, net cost savings on the test cohort
          total <strong>${financial.net_impact.toLocaleString()}</strong>.
          The system is production-ready subject to quarterly fairness audits and monthly PSI monitoring.
        </p>
      </div>

      <div className="exec-section">
        <h3>Model Performance</h3>
        <div className="kpi-row">
          {kpis.map((k, i) => (
            <div className="kpi-card" key={i}>
              <span className="kpi-label">{k.label}</span>
              <span className="kpi-value" style={{ color: k.good(k.value) ? "#22c55e" : "#ef4444" }}>
                {k.fmt(k.value)}
              </span>
            </div>
          ))}
        </div>
        <div className="table-wrap" style={{ marginTop: 16 }}>
          <table className="rg-table">
            <thead><tr><th>TP</th><th>FP</th><th>FN</th><th>TN</th></tr></thead>
            <tbody>
              <tr>
                <td style={{ color: "#22c55e" }}>{metrics.tp.toLocaleString()}</td>
                <td style={{ color: "#ef4444" }}>{metrics.fp.toLocaleString()}</td>
                <td style={{ color: "#f97316" }}>{metrics.fn.toLocaleString()}</td>
                <td style={{ color: "#3b82f6" }}>{metrics.tn.toLocaleString()}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="exec-section">
        <h3>Business Impact & Financial Savings</h3>
        <div className="kpi-row">
          <div className="kpi-card">
            <span className="kpi-label">Exposure Avoided</span>
            <span className="kpi-value" style={{ color: "#22c55e" }}>${financial.avoided_exposure.toLocaleString()}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">FP Cost (Good Declined)</span>
            <span className="kpi-value" style={{ color: "#ef4444" }}>${financial.fp_cost.toLocaleString()}</span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">Net Financial Impact</span>
            <span className="kpi-value" style={{ color: financial.net_impact > 0 ? "#22c55e" : "#ef4444" }}>
              ${financial.net_impact.toLocaleString()}
            </span>
          </div>
          <div className="kpi-card">
            <span className="kpi-label">STP Reduction</span>
            <span className="kpi-value" style={{ color: "#3b82f6" }}>{financial.stp_reduction_pct}%</span>
          </div>
        </div>
      </div>

      <div className="exec-section">
        <h3>Fairness & Compliance Assessment</h3>
        <p className="exec-para">
          Fairness metrics are computed per region group using demographic parity ratio and equalized odds gap.
          All automated decisions include SHAP explanations (GDPR Article 22 compliant). Recommended: monitor
          parity ratio quarterly (target ≥ 0.80), log all manual overrides for disparate-impact auditing.
        </p>
      </div>

      <div className="exec-section">
        <h3>Recommendations for Underwriting Policy</h3>
        <ol className="rec-list">
          <li>Adopt STP below threshold <strong>{metrics.opt_threshold}</strong> — reduces manual review by ~{financial.stp_reduction_pct}% of applications.</li>
          <li>Escalate applications between <strong>{metrics.opt_threshold}–0.70</strong> to Senior UW with SHAP summary attached.</li>
          <li>Hard-decline or committee-review above <strong>0.70</strong> — loss ratio in this band typically exceeds 85%.</li>
          <li>Retrain quarterly using logged underwriter overrides as signal.</li>
          <li>Shadow-mode challenger model for 4 weeks before any production swap.</li>
        </ol>
      </div>

      <p className="fine-print">RiskGuard AI — Confidential. For internal underwriting use only.</p>
    </div>
  );
}

// ─── App Shell ───────────────────────────────────────────────

const NAV = [
  { id: "score",    label: "Single Application" },
  { id: "whatif",  label: "What-If Simulator"  },
  { id: "fairness",label: "Fairness Audit"      },
  { id: "report",  label: "Executive Report"    },
];

export default function App() {
  const [page, setPage]     = useState("score");
  const [appIdx, setAppIdx] = useState(0);
  const [maxIdx, setMax]    = useState(999);

  useEffect(() => {
    fetch(`${API}/sample_range`).then(r => r.json()).then(d => setMax(d.max_idx));
  }, []);

  return (
    <div className="rg-root">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <div>
            <p className="logo-title">RiskGuard</p>
            <p className="logo-sub">Underwriting Intelligence</p>
          </div>
        </div>
        <nav>
          {NAV.map(n => (
            <button key={n.id} className={`nav-btn ${page === n.id ? "active" : ""}`}
              onClick={() => setPage(n.id)}>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>Model live · RF v2.0</span>
        </div>
      </aside>

      <main className="main-content">
        {page === "score"    && <SingleApplication appIdx={appIdx} setAppIdx={setAppIdx} maxIdx={maxIdx} />}
        {page === "whatif"  && <WhatIfSimulator   appIdx={appIdx} />}
        {page === "fairness"&& <FairnessAudit />}
        {page === "report"  && <ExecutiveReport />}
      </main>
    </div>
  );
}
