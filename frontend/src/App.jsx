import { useState } from "react";
import Home from "./pages/Home";
import Predict from "./pages/Predict";
import Results from "./pages/Results";
import About from "./pages/About";
import Navbar from "./components/Navbar";
import "./App.css";
import Weather from "./pages/Weather";

export default function App() {
  const [page, setPage] = useState("home");
  const [predictionResult, setPredictionResult] = useState(null);

  const navigate = (p) => {
    setPage(p);
    window.scrollTo(0, 0);
  };

  const handlePrediction = (result) => {
    setPredictionResult(result);
    navigate("results");
  };

  return (
    <div className="app">
      <Navbar currentPage={page} navigate={navigate} />
      <main>
        {page === "home"    && <Home navigate={navigate} />}
        {page === "predict" && <Predict onResult={handlePrediction} />}
        {page === "results" && <Results result={predictionResult} navigate={navigate} />}
        {page === "about"   && <About />}
        {page === "Weather"   && <Weather/>}
      </main>
    </div>
  );
}
