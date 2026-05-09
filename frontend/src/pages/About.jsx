export default function About() {
  const team = [
    { emoji: "👨‍💻", name: "Kushal Chakraborty", role: "ML Engineer", desc: "Designed and trained the Random Forest model, data preprocessing pipeline, and API." },
    { emoji: "🎨", name: "Shuvonkar Routh", role: "Frontend Developer", desc: "Built the React web application, UI/UX design, and API integration." },
    { emoji: "📊", name: "Boudi", role: "Data Analyst", desc: "Handled dataset collection, exploratory data analysis, and model evaluation." },
  ];

  const techStack = [
    "Python 3.10", "scikit-learn", "pandas", "NumPy",
    "Flask", "Flask-CORS", "React 18", "Vite",
    "Render.com", "Vercel", "GitHub", "Joblib",
  ];

  return (
    <div className="about-page">
      {/* Hero */}
      <div className="about-hero">
        <div className="about-hero-text">
          <h1>About This Project</h1>
          <p>
            CropYield AI is an MCA final year project that applies machine learning
            to one of India's most critical sectors — agriculture. By predicting
            crop yields based on environmental and soil conditions, we aim to help
            farmers, researchers, and policymakers make data-driven decisions.
          </p>
          <p style={{ marginTop: "16px" }}>
            Built using a Random Forest regression model achieving ~94% accuracy,
            backed by a Flask REST API and a modern React frontend.
          </p>
        </div>
        <div className="about-hero-icon">🌾</div>
      </div>

      {/* Team */}
      <div className="section-header" style={{ textAlign: "left", marginBottom: "32px" }}>
        <h2>Our Team</h2>
        <p style={{ color: "var(--text-light)" }}>MCA Students — [guru nanak institute of Technology]</p>
      </div>

      <div className="team-grid" style={{ marginBottom: "60px" }}>
        {team.map((m, i) => (
          <div className="team-card" key={i}>
            <div className="team-avatar">{m.emoji}</div>
            <h3>{m.name}</h3>
            <div className="role">{m.role}</div>
            <p>{m.desc}</p>
          </div>
        ))}
      </div>

      {/* Tech Stack */}
      <div className="detail-card">
        <h3>🛠️ Technology Stack</h3>
        <p style={{ fontSize: "0.92rem", color: "var(--text-light)", marginBottom: "16px" }}>
          This project was built using the following tools and technologies:
        </p>
        <div className="tech-stack">
          {techStack.map(t => <span className="tech-tag" key={t}>{t}</span>)}
        </div>
      </div>

      {/* Methodology */}
      <div className="detail-card" style={{ marginTop: "24px" }}>
        <h3>📐 Methodology</h3>
        <div className="detail-row"><span>Dataset Size</span><span>2000+ samples</span></div>
        <div className="detail-row"><span>Train / Test Split</span><span>80% / 20%</span></div>
        <div className="detail-row"><span>Best Model</span><span>Random Forest Regressor</span></div>
        <div className="detail-row"><span>R² Score</span><span>~0.94</span></div>
        <div className="detail-row"><span>MAE</span><span>~0.18 tons/hectare</span></div>
        <div className="detail-row"><span>Features Used</span><span>10 input features</span></div>
        <div className="detail-row"><span>Evaluation Metric</span><span>R², MAE, RMSE</span></div>
      </div>

      {/* Supervisor */}
      <div className="detail-card" style={{ marginTop: "24px" }}>
        <h3>🎓 Academic Details</h3>
        <div className="detail-row"><span>Program</span><span>Master of Computer Applications (MCA)</span></div>
        <div className="detail-row"><span>Institution</span><span>[Guru Nanak Institute Of Technology]</span></div>
        <div className="detail-row"><span>Academic Year</span><span>2024–2026</span></div>
        <div className="detail-row"><span>Guide / Supervisor</span><span>[Indranil sir]</span></div>
        <div className="detail-row"><span>Project Type</span><span>Final Year Project</span></div>
      </div>
    </div>
  );
}
