import { useState, useEffect } from "react";

const API = "http://localhost:5000";

const WB_DISTRICTS = [
  "Kolkata","Darjeeling","Siliguri","Murshidabad","Burdwan",
  "Midnapore","Howrah","Bankura","Purulia","Cooch Behar","Malda","Nadia","Bangaon"
];

const WEATHER_CODES = {
  0:"☀️ Clear Sky", 1:"🌤️ Mainly Clear", 2:"⛅ Partly Cloudy", 3:"☁️ Overcast",
  45:"🌫️ Fog", 48:"🌫️ Depositing Rime Fog",
  51:"🌦️ Light Drizzle", 53:"🌦️ Moderate Drizzle", 55:"🌧️ Dense Drizzle",
  61:"🌧️ Slight Rain", 63:"🌧️ Moderate Rain", 65:"🌧️ Heavy Rain",
  80:"🌦️ Slight Showers", 81:"🌧️ Moderate Showers", 82:"⛈️ Violent Showers",
  95:"⛈️ Thunderstorm", 96:"⛈️ Thunderstorm + Hail",
};

const CROP_ADVISORY = (temp, humidity, rain) => {
  const tips = [];
  if (temp > 38) tips.push({ icon:"🌡️", text:"Very high temperature — irrigate crops early morning or evening to reduce heat stress." });
  if (temp < 15) tips.push({ icon:"❄️", text:"Low temperature — protect seedlings with mulching. Good for Rabi crops like wheat." });
  if (humidity > 85) tips.push({ icon:"💧", text:"High humidity — watch for fungal diseases. Spray preventive fungicide on rice and potato." });
  if (rain > 10)  tips.push({ icon:"🌧️", text:"Heavy rainfall expected — ensure proper field drainage to prevent waterlogging." });
  if (rain < 1 && temp > 30) tips.push({ icon:"☀️", text:"Dry & hot — irrigation needed. Check soil moisture daily." });
  if (tips.length === 0) tips.push({ icon:"✅", text:"Weather conditions are favorable for most crops. Continue normal farm activities." });
  return tips;
};

export default function Weather() {
  const [district, setDistrict] = useState("Bangaon");
  const [data, setData]         = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const fetchWeather = async (d) => {
    setLoading(true); setError(""); setData(null);
    try {
      const res = await fetch(`${API}/weather?district=${encodeURIComponent(d)}`);
      const json = await res.json();
      if (json.error && !json.fallback) { setError(json.error); }
      else { setData(json); }
    } catch {
      setError("Cannot connect to backend. Start Flask: python app.py");
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchWeather(district); }, []);

  const handleChange = (e) => { setDistrict(e.target.value); fetchWeather(e.target.value); };

  const cur = data?.current || {};
  const forecast = data?.forecast_7days || [];
  const advisory = data ? CROP_ADVISORY(cur.temperature || 30, cur.humidity || 70, forecast[0]?.rain_mm || 0) : [];

  return (
    <div className="feature-page">
      <div className="feature-header">
        <h1>🌦️ Live Weather — West Bengal</h1>
        <p>Real-time weather data for farming decisions across all West Bengal districts.</p>
      </div>

      {/* District Selector */}
      <div className="weather-controls">
        <div className="form-field" style={{ maxWidth: 300 }}>
          <label>Select District</label>
          <select value={district} onChange={handleChange} className="district-select">
            {WB_DISTRICTS.map(d => <option key={d}>{d}</option>)}
          </select>
        </div>
        <button className="btn-primary" onClick={() => fetchWeather(district)} style={{ alignSelf:"flex-end" }}>
          🔄 Refresh
        </button>
      </div>

      {loading && <div className="loading-card">⏳ Fetching live weather for {district}...</div>}
      {error   && <div className="error-banner">⚠️ {error}</div>}

      {data && (
        <>
          {/* Current Weather */}
          <div className="weather-current">
            <div className="weather-main">
              <div className="weather-temp">{cur.temperature ?? "—"}°C</div>
              <div className="weather-desc">{WEATHER_CODES[cur.weather_code] ?? "🌤️"}</div>
              <div className="weather-location">📍 {district}, West Bengal</div>
            </div>
            <div className="weather-details-grid">
              <div className="weather-detail-item">
                <span className="wd-icon">💧</span>
                <span className="wd-val">{cur.humidity ?? "—"}%</span>
                <span className="wd-lbl">Humidity</span>
              </div>
              <div className="weather-detail-item">
                <span className="wd-icon">🌧️</span>
                <span className="wd-val">{cur.precipitation ?? "0"} mm</span>
                <span className="wd-lbl">Precipitation</span>
              </div>
              <div className="weather-detail-item">
                <span className="wd-icon">💨</span>
                <span className="wd-val">{cur.wind_speed ?? "—"} km/h</span>
                <span className="wd-lbl">Wind Speed</span>
              </div>
            </div>
          </div>

          {/* 7-Day Forecast */}
          {forecast.length > 0 && (
            <div className="section-card">
              <h3>📅 7-Day Forecast</h3>
              <div className="forecast-grid">
                {forecast.map((day, i) => (
                  <div className="forecast-day" key={i}>
                    <div className="forecast-date">{new Date(day.date).toLocaleDateString('en-IN',{weekday:'short',day:'numeric',month:'short'})}</div>
                    <div className="forecast-icon">{day.rain_mm > 5 ? "🌧️" : day.rain_mm > 1 ? "🌦️" : "☀️"}</div>
                    <div className="forecast-temp">{day.temp_max}° / {day.temp_min}°</div>
                    <div className="forecast-rain">🌧 {day.rain_mm} mm</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Crop Advisory */}
          <div className="section-card advisory-card">
            <h3>🌾 Crop Advisory for Today</h3>
            <div className="advisory-list">
              {advisory.map((tip, i) => (
                <div className="advisory-item" key={i}>
                  <span className="advisory-icon">{tip.icon}</span>
                  <span>{tip.text}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}