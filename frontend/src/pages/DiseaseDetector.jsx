import { useState, useRef } from "react";

const API = "http://localhost:5000";

const CROPS = ['Rice','Wheat','Maize','Soybean','Cotton','Sugarcane','Potato','Tomato'];

const SEVERITY_STYLE = {
  "None":           { bg:"#d8f3dc", color:"#2d6a4f", label:"Healthy" },
  "Low-Moderate":   { bg:"#fff3cd", color:"#856404", label:"Low Risk" },
  "Moderate":       { bg:"#ffe5b4", color:"#d4820a", label:"Moderate" },
  "High":           { bg:"#ffd6d6", color:"#c0392b", label:"High Risk" },
};

export default function DiseaseDetector() {
  const [image, setImage]     = useState(null);
  const [preview, setPreview] = useState(null);
  const [crop, setCrop]       = useState("Rice");
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const fileRef = useRef();

  const handleFile = (file) => {
    if (!file) return;
    setImage(file); setResult(null); setError("");
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const detect = async () => {
    if (!image) { setError("Please upload a leaf image first."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("crop", crop);
      const res  = await fetch(`${API}/disease-detect`, { method:"POST", body:formData });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError("Cannot connect to backend. Start Flask: python app.py");
    } finally { setLoading(false); }
  };

  const sev = result ? (SEVERITY_STYLE[result.severity] || SEVERITY_STYLE["Moderate"]) : null;

  return (
    <div className="feature-page">
      <div className="feature-header">
        <h1>🔬 Crop Disease Detector</h1>
        <p>Upload a leaf photo and get instant AI-powered disease diagnosis with treatment advice.</p>
      </div>

      <div className="analyzer-layout">
        {/* Upload Panel */}
        <div className="upload-panel">
          <div style={{ marginBottom:20 }}>
            <label style={{
              display:"block", fontSize:"0.82rem", fontWeight:600,
              color:"var(--text-mid)", marginBottom:8, letterSpacing:"0.3px"
            }}>
              🌿 Crop Type
            </label>
            <select value={crop} onChange={e => setCrop(e.target.value)}
              style={{
                width:"100%", padding:"12px 16px",
                borderRadius:10, border:"1.5px solid var(--cream-dark)",
                background:"var(--cream)", fontFamily:"'DM Sans', sans-serif",
                fontSize:"0.95rem", color:"var(--text-dark)",
                outline:"none", cursor:"pointer",
                appearance:"none",
                backgroundImage:`url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%232d6a4f' d='M6 8L1 3h10z'/%3E%3C/svg%3E")`,
                backgroundRepeat:"no-repeat",
                backgroundPosition:"right 14px center",
                paddingRight:36,
              }}>
              {CROPS.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>

          <div
            className={`drop-zone ${preview ? "has-preview" : ""}`}
            onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileRef.current.click()}
          >
            {preview ? (
              <img src={preview} alt="Leaf preview" className="soil-preview-img" />
            ) : (
              <>
                <div className="drop-icon">🍃</div>
                <div className="drop-text">Drop leaf image here</div>
                <div className="drop-sub">or click to browse</div>
                <div className="drop-hint">Best: close-up of a single leaf, JPG or PNG</div>
              </>
            )}
          </div>
          <input type="file" ref={fileRef} accept="image/*" style={{ display:"none" }}
            onChange={(e) => handleFile(e.target.files[0])} />

          {preview && (
            <button className="btn-outline" style={{ width:"100%", marginTop:12 }}
              onClick={() => { setPreview(null); setImage(null); setResult(null); }}>
              🗑️ Remove Image
            </button>
          )}

          <button className="btn-primary" style={{ width:"100%", marginTop:12 }}
            onClick={detect} disabled={loading || !image}>
            {loading ? "⏳ Detecting..." : "🔬 Detect Disease"}
          </button>

          {error && <div className="error-banner" style={{ marginTop:12 }}>⚠️ {error}</div>}

          <div className="tips-box">
            <h4>📸 Photo Tips</h4>
            <ul>
              <li>Use a single leaf, placed flat</li>
              <li>Bright natural light works best</li>
              <li>Show affected area clearly</li>
              <li>Avoid blurry or dark photos</li>
            </ul>
          </div>
        </div>

        {/* Results Panel */}
        <div className="result-panel">
          {!result && !loading && (
            <div className="result-empty">
              <div style={{ fontSize:"4rem" }}>🍃</div>
              <p>Upload a leaf image to diagnose crop diseases instantly.</p>
            </div>
          )}

          {result && (
            <>
              {/* Disease Badge */}
              <div className="soil-result-badge" style={{ background: sev.bg }}>
                <div className="soil-type-label" style={{ color: sev.color }}>Disease Detected</div>
                <div className="soil-type-name" style={{ color: sev.color }}>
                  {result.color_emoji} {result.disease.replace(/_/g, " ")}
                </div>
                <div className="soil-confidence">
                  Confidence: <strong>{result.confidence}%</strong> &nbsp;|&nbsp;
                  Severity: <strong style={{ color:sev.color }}>{sev.label}</strong>
                </div>
              </div>

              <div className="conf-bar-wrap">
                <div className="conf-bar" style={{ width:`${result.confidence}%`, background: sev.color }} />
              </div>

              {/* Description */}
              <div className="section-card" style={{ marginTop:20 }}>
                <h3>📋 Diagnosis</h3>
                <p style={{ fontSize:"0.92rem", color:"var(--text-mid)", lineHeight:1.7 }}>{result.description}</p>
                <div className="detail-row" style={{ marginTop:12 }}>
                  <span>Detected Crop</span>
                  <span style={{ fontWeight:600, color:"var(--green-dark)" }}>{result.detected_crop || result.crop}</span>
                </div>
                <div className="detail-row">
                  <span>Commonly Affects</span>
                  <span>{result.affected_crops?.join(", ")}</span>
                </div>
                <div className="detail-row">
                  <span>Detection Method</span>
                  <span style={{ color:"var(--green-mid)", fontWeight:600 }}>{result.method}</span>
                </div>
              </div>

              {/* Treatment */}
              <div className="section-card advisory-card">
                <h3>💊 Treatment</h3>
                <p style={{ fontSize:"0.92rem", color:"var(--text-mid)", lineHeight:1.7 }}>{result.treatment}</p>
              </div>

              {/* Prevention */}
              <div className="section-card">
                <h3>🛡️ Prevention</h3>
                <p style={{ fontSize:"0.92rem", color:"var(--text-mid)", lineHeight:1.7 }}>{result.prevention}</p>
              </div>

              {/* CNN Score Breakdown */}
              <div className="section-card">
                <h3>📊 CNN Confidence Scores</h3>
                {Object.entries(result.pixel_analysis || {}).sort((a,b)=>b[1]-a[1]).map(([key, val]) => (
                  <div key={key} style={{ marginBottom:12 }}>
                    <div style={{ display:"flex", justifyContent:"space-between", fontSize:"0.88rem", marginBottom:4 }}>
                      <span style={{ fontWeight: key === result.disease ? 600 : 400,
                        color: key === result.disease ? "var(--green-dark)" : "var(--text-mid)" }}>
                        {key === result.disease ? "🎯 " : ""}{key.replace(/_/g," ")}
                      </span>
                      <span style={{ fontWeight:600 }}>{val}%</span>
                    </div>
                    <div style={{ background:"var(--cream-dark)", borderRadius:8, height:8 }}>
                      <div style={{
                        width:`${Math.min(val, 100)}%`,
                        background: key === result.disease ? sev.color : "#c8e6c9",
                        height:8, borderRadius:8, transition:"width 0.5s"
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}