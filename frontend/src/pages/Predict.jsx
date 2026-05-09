import { useState, useEffect } from "react";

const API = "http://localhost:5000";

const DEFAULTS = {
  crops:   ['Cotton','Maize','Potato','Rice','Soybean','Sugarcane','Tomato','Wheat'],
  soils:   ['Clay','Loamy','Peaty','Sandy','Silt'],
  seasons: ['Kharif','Rabi','Zaid'],
  states:  ['Bihar','Haryana','Karnataka','MP','Maharashtra','Punjab','UP','West Bengal'],
};

export default function Predict({ onResult }) {
  const [options, setOptions]   = useState(DEFAULTS);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const [form, setForm] = useState({
    crop:           "Rice",
    soil_type:      "Loamy",
    season:         "Kharif",
    state:          "West Bengal",
    rainfall_mm:    1200,
    temperature:    28,
    humidity:       75,
    fertilizer_kg:  150,
    pesticide_kg:   2.5,
    area_hectares:  5,
  });

  // Try to load options from live API
  useEffect(() => {
    fetch(`${API}/options`)
      .then(r => r.json())
      .then(d => { if (d.crops) setOptions(d); })
      .catch(() => {}); // fallback to DEFAULTS silently
  }, []);

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const handleSubmit = async () => {
    setError("");
    setLoading(true);
    try {
      const payload = {
        ...form,
        rainfall_mm:   parseFloat(form.rainfall_mm),
        temperature:   parseFloat(form.temperature),
        humidity:      parseFloat(form.humidity),
        fertilizer_kg: parseFloat(form.fertilizer_kg),
        pesticide_kg:  parseFloat(form.pesticide_kg),
        area_hectares: parseFloat(form.area_hectares),
      };

      const res = await fetch(`${API}/predict`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        setError(data.error || "Prediction failed. Is the Flask server running?");
      } else {
        onResult({ ...data, input: form });
      }
    } catch {
      setError("Cannot connect to server. Start Flask: python app.py");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="predict-page">
      <div className="predict-header">
        <h1>🌾 Crop Yield Predictor</h1>
        <p>Fill in your farm details below to get an AI-powered yield prediction.</p>
      </div>

      <div className="predict-layout">
        {/* ── FORM ── */}
        <div className="predict-form-card">

          {/* Crop Details */}
          <div className="form-section-title">Crop Details</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Crop Type</label>
              <select value={form.crop} onChange={e => set("crop", e.target.value)}>
                {options.crops.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Season</label>
              <select value={form.season} onChange={e => set("season", e.target.value)}>
                {options.seasons.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Soil Type</label>
              <select value={form.soil_type} onChange={e => set("soil_type", e.target.value)}>
                {options.soils.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>State / Region</label>
              <select value={form.state} onChange={e => set("state", e.target.value)}>
                {options.states.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-field">
              <label>Farm Area (Hectares)</label>
              <input type="number" min="0.1" step="0.5"
                value={form.area_hectares}
                onChange={e => set("area_hectares", e.target.value)}
              />
            </div>
          </div>

          {/* Climate */}
          <div className="form-section-title">Climate & Environment</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Annual Rainfall (mm)</label>
              <input type="number" min="100" max="5000"
                value={form.rainfall_mm}
                onChange={e => set("rainfall_mm", e.target.value)}
                placeholder="e.g. 1200"
              />
            </div>
            <div className="form-field">
              <label>Average Temperature (°C)</label>
              <input type="number" min="-5" max="55"
                value={form.temperature}
                onChange={e => set("temperature", e.target.value)}
                placeholder="e.g. 28"
              />
            </div>
            <div className="form-field full">
              <label>Humidity (%)</label>
              <input type="number" min="10" max="100"
                value={form.humidity}
                onChange={e => set("humidity", e.target.value)}
                placeholder="e.g. 75"
              />
            </div>
          </div>

          {/* Inputs */}
          <div className="form-section-title">Farm Inputs</div>
          <div className="form-grid">
            <div className="form-field">
              <label>Fertilizer Used (kg/hectare)</label>
              <input type="number" min="0"
                value={form.fertilizer_kg}
                onChange={e => set("fertilizer_kg", e.target.value)}
                placeholder="e.g. 150"
              />
            </div>
            <div className="form-field">
              <label>Pesticide Used (kg/hectare)</label>
              <input type="number" min="0" step="0.1"
                value={form.pesticide_kg}
                onChange={e => set("pesticide_kg", e.target.value)}
                placeholder="e.g. 2.5"
              />
            </div>
          </div>

          {error && <div className="error-banner">⚠️ {error}</div>}

          <button className="predict-btn" onClick={handleSubmit} disabled={loading}>
            {loading ? "⏳ Predicting..." : "🔍 Predict Yield Now"}
          </button>
        </div>

        {/* ── SIDEBAR ── */}
        <div className="predict-sidebar">
          <div className="sidebar-card">
            <h3>🤖 ML Model</h3>
            <div className="model-badge">
              <div className="model-badge-icon">🌲</div>
              <div>
                <div className="model-badge-label">Algorithm</div>
                <div className="model-badge-value">Random Forest</div>
              </div>
            </div>
            <div className="model-badge">
              <div className="model-badge-icon">📈</div>
              <div>
                <div className="model-badge-label">Accuracy (R²)</div>
                <div className="model-badge-value">~94%</div>
              </div>
            </div>
            <div className="model-badge">
              <div className="model-badge-icon">📉</div>
              <div>
                <div className="model-badge-label">Avg Error (MAE)</div>
                <div className="model-badge-value">±0.18 tons/ha</div>
              </div>
            </div>
          </div>

          <div className="sidebar-card">
            <h3>💡 Tips for Accuracy</h3>
            <ul className="tip-list">
              <li><span>🌧️</span><span>Use annual average rainfall, not single-event data.</span></li>
              <li><span>🌡️</span><span>Temperature should be the seasonal average, not peak.</span></li>
              <li><span>🧪</span><span>Enter fertilizer per hectare, not total farm quantity.</span></li>
              <li><span>📍</span><span>Selecting the correct state improves regional accuracy.</span></li>
            </ul>
          </div>

          <div className="sidebar-card">
            <h3>📋 Sample Values</h3>
            <ul className="tip-list">
              <li><span>🌾</span><span><strong>Rice (Kharif):</strong> 1400mm rain, 30°C, 80% humidity</span></li>
              <li><span>🌿</span><span><strong>Wheat (Rabi):</strong> 600mm rain, 20°C, 55% humidity</span></li>
              <li><span>🌽</span><span><strong>Maize (Kharif):</strong> 900mm rain, 27°C, 70% humidity</span></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
