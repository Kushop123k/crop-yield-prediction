import { useState } from "react";

const API = "http://localhost:5000";

const CROPS   = ['Rice','Wheat','Maize','Soybean','Cotton','Sugarcane','Potato','Tomato'];
const SEASONS = ['Kharif','Rabi','Zaid'];
const STATES  = ['West Bengal','Punjab','UP','Maharashtra','Karnataka','Bihar','MP','Haryana'];

export default function Seeds() {
  const [crop,   setCrop]   = useState("Rice");
  const [season, setSeason] = useState("Kharif");
  const [state,  setState]  = useState("West Bengal");
  const [result, setResult] = useState(null);
  const [loading,setLoading]= useState(false);
  const [error,  setError]  = useState("");

  const fetch_ = async () => {
    setLoading(true); setError(""); setResult(null);
    try {
      const res  = await fetch(`${API}/seeds?crop=${crop}&season=${season}&state=${encodeURIComponent(state)}`);
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError("Cannot connect to backend. Start Flask: python app.py");
    } finally { setLoading(false); }
  };

  return (
    <div className="feature-page">
      <div className="feature-header">
        <h1>🌱 Seed & Fertilizer Guide</h1>
        <p>Get certified seed varieties, fertilizer doses, and pesticide recommendations for your crop.</p>
      </div>

      {/* Filter Card */}
      <div className="section-card" style={{ marginBottom:28 }}>
        <div className="form-grid" style={{ marginBottom:20 }}>
          <div className="form-field">
            <label>Crop</label>
            <select value={crop} onChange={e => setCrop(e.target.value)}>
              {CROPS.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-field">
            <label>Season</label>
            <select value={season} onChange={e => setSeason(e.target.value)}>
              {SEASONS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div className="form-field">
            <label>State</label>
            <select value={state} onChange={e => setState(e.target.value)}>
              {STATES.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
        </div>
        <button className="btn-primary" onClick={fetch_} disabled={loading}>
          {loading ? "⏳ Loading..." : "🔍 Get Recommendations"}
        </button>
        {error && <div className="error-banner" style={{ marginTop:12 }}>⚠️ {error}</div>}
      </div>

      {result && (
        <>
          {/* Seed Varieties */}
          <div className="section-card">
            <h3>🌾 Certified Seed Varieties — {result.crop} ({result.season})</h3>
            <p style={{ fontSize:"0.85rem", color:"var(--text-light)", marginBottom:20 }}>
              Recommendations for <strong>{result.state}</strong> based on ICAR & state agriculture guidelines.
            </p>
            <div className="seed-grid">
              {result.varieties.map((v, i) => (
                <div className="seed-card" key={i}>
                  <div className="seed-rank">#{i+1}</div>
                  <div className="seed-name">{v.name}</div>
                  <div className="seed-trait">{v.trait}</div>
                  <div className="seed-details">
                    <span>⏱ {v.duration}</span>
                    <span>📦 {v.yield}</span>
                  </div>
                  {v.certified && <div className="seed-certified">✅ ICAR Certified</div>}
                </div>
              ))}
            </div>
          </div>

          {/* Fertilizer */}
          <div className="section-card" style={{ marginTop:24 }}>
            <h3>🧪 Fertilizer Recommendation (per hectare)</h3>
            <div className="npk-grid">
              <div className="npk-card" style={{ background:"#e8f5e9" }}>
                <div className="npk-label">Nitrogen (N)</div>
                <div className="npk-value">{result.fertilizer.N} kg</div>
              </div>
              <div className="npk-card" style={{ background:"#fff3e0" }}>
                <div className="npk-label">Phosphorus (P)</div>
                <div className="npk-value">{result.fertilizer.P} kg</div>
              </div>
              <div className="npk-card" style={{ background:"#e3f2fd" }}>
                <div className="npk-label">Potassium (K)</div>
                <div className="npk-value">{result.fertilizer.K} kg</div>
              </div>
            </div>
            <div className="advisory-item" style={{ marginTop:16 }}>
              <span className="advisory-icon">💡</span>
              <span style={{ fontSize:"0.92rem", color:"var(--text-mid)" }}>{result.fertilizer.note}</span>
            </div>
          </div>

          {/* Pesticides */}
          {result.pesticides?.length > 0 && (
            <div className="section-card" style={{ marginTop:24 }}>
              <h3>🐛 Pest & Disease Management</h3>
              <div className="pest-table">
                <div className="pest-header">
                  <span>Pest / Disease</span>
                  <span>Recommended Chemical</span>
                  <span>Dose</span>
                </div>
                {result.pesticides.map((p, i) => (
                  <div className="pest-row" key={i}>
                    <span>🦠 {p.pest}</span>
                    <span>{p.chemical}</span>
                    <span className="pest-dose">{p.dose}</span>
                  </div>
                ))}
              </div>
              <p style={{ fontSize:"0.82rem", color:"var(--text-light)", marginTop:12 }}>
                ⚠️ Always follow label instructions. Use PPE while spraying. Observe pre-harvest intervals.
              </p>
            </div>
          )}

          <p style={{ fontSize:"0.8rem", color:"var(--text-light)", marginTop:16 }}>{result.source_note}</p>
        </>
      )}
    </div>
  );
}
