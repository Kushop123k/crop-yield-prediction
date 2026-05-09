export default function Home({ navigate }) {
  const features = [
    { icon: "🤖", title: "Machine Learning Powered", desc: "Random Forest model trained on thousands of agricultural data points for high-accuracy predictions." },
    { icon: "🌦️", title: "Climate-Aware Predictions", desc: "Factors in rainfall, temperature, and humidity to give seasonally accurate yield estimates." },
    { icon: "🌱", title: "Multi-Crop Support", desc: "Supports 8 major crops including Rice, Wheat, Maize, Sugarcane, Cotton, Potato, and more." },
    { icon: "🗺️", title: "Region-Specific", desc: "Tailored for Indian agricultural zones including West Bengal, Punjab, Maharashtra, and 5 more states." },
    { icon: "⚡", title: "Instant Results", desc: "Get yield predictions in under a second via our optimized REST API backend." },
    { icon: "📊", title: "Detailed Analytics", desc: "Receive per-hectare yield, total yield, and input breakdown with every prediction." },
  ];

  const steps = [
    { num: "1", title: "Enter Farm Details", desc: "Provide crop type, soil, season, and location information." },
    { num: "2", title: "Set Climate Data", desc: "Input rainfall, temperature, and humidity values." },
    { num: "3", title: "Get Prediction", desc: "Our ML model predicts your expected crop yield instantly." },
  ];

  return (
    <>
      {/* HERO */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            🏆 MCA Final Year Project — 2026
          </div>
          <h1>
            Predict Your<br />
            <span>Crop Yield</span><br />
            with AI
          </h1>
          <p>
            An intelligent machine learning system that predicts agricultural
            yield based on soil, climate, and farming conditions — helping
            farmers and researchers make smarter decisions.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={() => navigate("predict")}>
              🌾 Start Predicting
            </button>
            <button className="btn-secondary" onClick={() => navigate("about")}>
              Learn More
            </button>
          </div>
        </div>
        <div className="hero-visual">🌾</div>
      </section>

      {/* STATS */}
      <div className="stats-bar">
        {[
          { num: "8+",   label: "Crop Varieties Supported" },
          { num: "8",    label: "Indian States Covered" },
          { num: "94%",  label: "Model Accuracy (R²)" },
          { num: "2000+",label: "Training Data Points" },
        ].map((s, i) => (
          <div className="stat-item" key={i}>
            <div className="stat-number">{s.num}</div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* FEATURES */}
      <section className="section">
        <div className="section-header">
          <h2>Why CropYield AI?</h2>
          <p>Built with modern ML techniques and a clean web interface to make agricultural prediction accessible to everyone.</p>
        </div>
        <div className="features-grid">
          {features.map((f, i) => (
            <div className="feature-card" key={i}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="section section-alt">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Three simple steps to get your crop yield prediction.</p>
        </div>
        <div className="steps">
          {steps.map((s, i) => (
            <div className="step" key={i}>
              <div className="step-num">{s.num}</div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>
        <div style={{ textAlign: "center", marginTop: "48px" }}>
          <button className="btn-primary" onClick={() => navigate("predict")}>
            Try It Now →
          </button>
        </div>
      </section>
    </>
  );
}
