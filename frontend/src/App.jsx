import { useState } from "react";
import Home            from "./pages/Home";
import Predict         from "./pages/Predict";
import Results         from "./pages/Results";
import About           from "./pages/About";
import Weather         from "./pages/Weather";
import SoilAnalyzer    from "./pages/SoilAnalyzer";
import DiseaseDetector from "./pages/DiseaseDetector";
import Seeds           from "./pages/Seeds";
import Navbar          from "./components/Navbar";
import "./App.css";

export default function App() {
  const [page, setPage]                   = useState("home");
  const [predictionResult, setPrediction] = useState(null);

  const navigate = (p) => { setPage(p); window.scrollTo(0, 0); };

  const handlePrediction = (result) => {
    setPrediction(result);
    navigate("results");
  };

  return (
    <div className="app">
      <Navbar currentPage={page} navigate={navigate} />
      <main>
        {page === "home"    && <Home navigate={navigate} />}
        {page === "predict" && <Predict onResult={handlePrediction} />}
        {page === "results" && <Results result={predictionResult} navigate={navigate} />}
        {page === "weather" && <Weather />}
        {page === "soil"    && <SoilAnalyzer />}
        {page === "disease" && <DiseaseDetector />}
        {page === "seeds"   && <Seeds />}
        {page === "about"   && <About />}
      </main>
    </div>
  );
}
