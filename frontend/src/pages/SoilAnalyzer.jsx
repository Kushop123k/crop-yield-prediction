import { useState, useRef } from "react";

const API = "http://localhost:5000";

export default function SoilAnalyzer() {
  const [image, setImage]     = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const fileRef = useRef();

  const handleFile = (file) => {
    if (!file) return;
    setImage(file);
    setResult(null);
    setError("");
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const analyze = async () => {
    if (!image) { setError("Please upload a soil image first."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const formData = new FormData();
      formData.append("image", image);
      const res  = await fetch(`${API}/soil-analyze`, { method: "POST", body: formData });
      const data = await res.json();
      if (data.error) setError(data.error);
      else setResult(data);
    } catch {
      setError("Cannot connect to backend. Start Flask: python app.py");
    } finally { setLoading(false); }
  };

  const FERTILITY_COLOR = { "High":"#2d6a4f", "Moderate-High":"#52b788", "Moderate":"#d4a373", "Low":"#e07a5f" };

  return (
    <div className="feature-page">
      <div className="feature-header">
        <h1>🪨 Soil Image Analyzer</h1>
        <p>Upload a soil photo and our AI will classify the soil type and recommend suitable crops.</p>
      </div>

      <div className="analyzer-layout">
        {/* Upload Panel */}
        <div className="upload-panel">
          <div
            className={`drop-zone ${preview ? "has-preview" : ""}`}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileRef.current.click()}
          >
            {preview ? (
              <img src={preview} alt="Soil preview" className="soil-preview-img" />
            ) : (
              <>
                <div className="drop-icon">🪨</div>
                <div className="drop-text">Drop soil image here</div>
                <div className="drop-sub">or click to browse</div>
                <div className="drop-hint">JPG, PNG up to 10MB</div>
              </>
            )}
          </div>
          <input
            type="file" ref={fileRef} accept="image/*" style={{ display:"none" }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
          {preview && (
            <button className="btn-outline" style={{ width:"100%", marginTop:12 }}
              onClick={() => { setPreview(null); setImage(null); setResult(null); }}>
              🗑️ Remove Image
            </button>
          )}
          <button className="btn-primary" style={{ width:"100%", marginTop:12 }}
            onClick={analyze} disabled={loading || !image}>
            {loading ? "⏳ Analyzing..." : "🔬 Analyze Soil"}
          </button>
          {error && <div className="error-banner" style={{ marginTop:12 }}>⚠️ {error}</div>}

          <div className="tips-box">
            <h4>📸 Photo Tips for Better Results</h4>
            <ul>
              <li>Take photo in natural daylight</li>
              <li>Show fresh/moist soil surface</li>
              <li>Avoid shadows on the soil</li>
              <li>Fill the frame with soil only</li>
            </ul>
          </div>
        </div>

        {/* Results Panel */}
        <div className="result-panel">
          {!result && !loading && (
            <div className="result-empty">
              <div style={{ fontSize:"4rem" }}>🔬</div>
              <p>Upload a soil image to see AI analysis results here.</p>
            </div>
          )}

          {result && (
            <>
              {/* Soil Type Badge */}
              <div className="soil-result-badge">
                <div className="soil-type-label">Detected Soil Type</div>
                <div className="soil-type-name">{result.soil_type}</div>
                <div className="soil-confidence">
                  Confidence: <strong>{result.confidence}%</strong>
                </div>
              </div>

              {/* Confidence Bar */}
              <div className="conf-bar-wrap">
                <div className="conf-bar" style={{ width:`${result.confidence}%`,
                  background: result.confidence > 80 ? "#2d6a4f" : result.confidence > 65 ? "#d4a373" : "#e07a5f" }} />
              </div>

              {/* Properties */}
              <div className="section-card" style={{ marginTop:20 }}>
                <h3>🧪 Soil Properties</h3>
                <div className="detail-row"><span>Description</span><span style={{ maxWidth:220, textAlign:"right", fontSize:"0.85rem" }}>{result.description}</span></div>
                <div className="detail-row"><span>Soil Color</span><span>{result.color_hint}</span></div>
                <div className="detail-row">
                  <span>Fertility</span>
                  <span style={{ color: FERTILITY_COLOR[result.fertility] || "#333", fontWeight:700 }}>{result.fertility}</span>
                </div>
                <div className="detail-row"><span>Water Retention</span><span>{result.water_retention}</span></div>
                <div className="detail-row"><span>pH Range</span><span>{result.ph_range}</span></div>
              </div>

              {/* Recommended Crops */}
              <div className="section-card">
                <h3>🌾 Recommended Crops</h3>
                <div className="crop-tags">
                  {result.recommended_crops.map((c) => (
                    <span className="crop-tag" key={c}>{c}</span>
                  ))}
                </div>
              </div>

              {/* Tips */}
              <div className="section-card advisory-card">
                <h3>💡 Farming Tips</h3>
                <p style={{ fontSize:"0.92rem", color:"var(--text-mid)", lineHeight:1.7 }}>{result.tips}</p>
              </div>

              {/* Color Analysis */}
              <div className="section-card">
                <h3>🎨 Color Analysis (HSV)</h3>
                <div className="detail-row"><span>Hue</span><span>{result.color_analysis?.hue}</span></div>
                <div className="detail-row"><span>Saturation</span><span>{result.color_analysis?.saturation}</span></div>
                <div className="detail-row"><span>Brightness</span><span>{result.color_analysis?.brightness}</span></div>
              </div>

              {/* Score breakdown */}
              <div className="section-card">
                <h3>📊 All Soil Scores</h3>
                {Object.entries(result.all_scores || {}).sort((a,b)=>b[1]-a[1]).map(([soil, score]) => (
                  <div key={soil} style={{ marginBottom:10 }}>
                    <div style={{ display:"flex", justifyContent:"space-between", fontSize:"0.88rem", marginBottom:4 }}>
                      <span>{soil}</span><span>{score}%</span>
                    </div>
                    <div style={{ background:"var(--cream-dark)", borderRadius:8, height:8 }}>
                      <div style={{ width:`${score}%`, background: soil === result.soil_type ? "var(--green-mid)" : "var(--green-pale)", height:8, borderRadius:8, transition:"width 0.5s" }} />
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
