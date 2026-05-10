import { useState } from "react";

export default function Navbar({ currentPage, navigate }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const links = [
    { id:"home",    label:"🏠 Home" },
    { id:"predict", label:"🌾 Predict" },
    { id:"weather", label:"🌦️ Weather" },
    { id:"soil",    label:"🪨 Soil AI" },
    { id:"disease", label:"🔬 Disease" },
    { id:"seeds",   label:"🌱 Seeds" },
    { id:"about",   label:"👥 About" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate("home")}>
        <span>🌾</span>
        <span className="navbar-logo-text">Crop<em>Yield</em> AI</span>
      </div>
      <div className="navbar-links">
        {links.map(l => (
          <button key={l.id} className={currentPage === l.id ? "active" : ""} onClick={() => navigate(l.id)}>
            {l.label}
          </button>
        ))}
      </div>
      <button className="hamburger" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? "✕" : "☰"}</button>
      {menuOpen && (
        <div className="mobile-menu">
          {links.map(l => (
            <button key={l.id} className={currentPage === l.id ? "active" : ""}
              onClick={() => { navigate(l.id); setMenuOpen(false); }}>{l.label}</button>
          ))}
        </div>
      )}
    </nav>
  );
}
