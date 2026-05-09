export default function Navbar({ currentPage, navigate }) {
  const links = [
    { id: "home",    label: "Home" },
    { id: "predict", label: "Predict" },
    { id: "about",   label: "About" },
    { id: "Weather",   label: "Weather" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate("home")}>
        <span>🌾</span>
        <span className="navbar-logo-text">Crop<em>Yield</em> AI</span>
      </div>

      <div className="navbar-links">
        {links.map(l => (
          <button
            key={l.id}
            className={currentPage === l.id ? "active" : ""}
            onClick={() => navigate(l.id)}
          >
            {l.label}
          </button>
        ))}
        <button className="navbar-cta" onClick={() => navigate("predict")}>
          Try Prediction →
        </button>
      </div>
    </nav>
  );
}
