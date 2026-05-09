export default function Results({ result, navigate }) {
  if (!result) {
    return (
      <div className="results-page">
        <p>No prediction yet. <button className="btn-outline" onClick={() => navigate("predict")}>Go to Predictor</button></p>
      </div>
    );
  }

  const { yield_per_hectare, total_yield_tons, area_hectares, crop, input } = result;

  const getYieldCategory = (y) => {
    if (y >= 10) return { label: "Excellent",  color: "#2d6a4f", emoji: "🌟" };
    if (y >= 5)  return { label: "Good",        color: "#52b788", emoji: "✅" };
    if (y >= 2)  return { label: "Average",     color: "#d4a373", emoji: "⚠️" };
    return       { label: "Below Average", color: "#c0392b", emoji: "📉" };
  };

  const category = getYieldCategory(yield_per_hectare);

  return (
    <div className="results-page">
      <div className="results-header">
        <h1>🌾 Prediction Results</h1>
        <p>Here's what our AI model predicted for your farm.</p>
      </div>

      {/* Summary Cards */}
      <div className="results-grid">
        <div className="result-card highlight">
          <div className="result-card-label">Yield Per Hectare</div>
          <div className="result-card-value">{yield_per_hectare}</div>
          <div className="result-card-unit">tons / hectare</div>
        </div>

        <div className="result-card">
          <div className="result-card-label">Total Expected Yield</div>
          <div className="result-card-value">{total_yield_tons}</div>
          <div className="result-card-unit">tons total ({area_hectares} hectares)</div>
        </div>

        <div className="result-card">
          <div className="result-card-label">Yield Category</div>
          <div className="result-card-value" style={{ fontSize: "2.8rem" }}>{category.emoji}</div>
          <div className="result-card-unit" style={{ color: category.color, fontWeight: 600, fontSize: "1rem" }}>{category.label}</div>
        </div>
      </div>

      {/* Details */}
      <div className="results-details">
        <div className="detail-card">
          <h3>🌱 Crop & Location Details</h3>
          <div className="detail-row"><span>Crop Type</span><span>{input.crop}</span></div>
          <div className="detail-row"><span>Season</span><span>{input.season}</span></div>
          <div className="detail-row"><span>Soil Type</span><span>{input.soil_type}</span></div>
          <div className="detail-row"><span>State</span><span>{input.state}</span></div>
          <div className="detail-row"><span>Farm Area</span><span>{input.area_hectares} hectares</span></div>
        </div>

        <div className="detail-card">
          <h3>🌦️ Climate & Input Details</h3>
          <div className="detail-row"><span>Rainfall</span><span>{input.rainfall_mm} mm</span></div>
          <div className="detail-row"><span>Temperature</span><span>{input.temperature} °C</span></div>
          <div className="detail-row"><span>Humidity</span><span>{input.humidity} %</span></div>
          <div className="detail-row"><span>Fertilizer</span><span>{input.fertilizer_kg} kg/ha</span></div>
          <div className="detail-row"><span>Pesticide</span><span>{input.pesticide_kg} kg/ha</span></div>
        </div>
      </div>

      {/* AI Note */}
      <div className="detail-card" style={{ marginTop: "24px" }}>
        <h3>📌 Interpretation</h3>
        <p style={{ fontSize: "0.95rem", color: "var(--text-mid)", lineHeight: 1.7 }}>
          Based on the given inputs, <strong>{crop}</strong> cultivation over <strong>{area_hectares} hectares</strong> is expected
          to yield approximately <strong>{yield_per_hectare} tons/hectare</strong>, totaling <strong>{total_yield_tons} tons</strong>.
          The yield is rated <strong style={{ color: category.color }}>{category.label}</strong>.
          This prediction was made using a Random Forest regression model trained on historical agricultural data.
          Results may vary based on actual field conditions, irrigation, and farming practices.
        </p>
      </div>

      <div className="results-actions">
        <button className="btn-primary" onClick={() => navigate("predict")}>
          🔄 Make Another Prediction
        </button>
        <button className="btn-outline" onClick={() => window.print()}>
          🖨️ Print / Save Report
        </button>
      </div>
    </div>
  );
}
