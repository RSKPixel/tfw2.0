import { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Basetemplate from "./templates/Basetemplate";
import GlobalContext from "./templates/GlobalContext";
import MarketData from "./pages/MarketData";
import Zerodha from "./pages/portfolio/Zerodha";

function App() {
  const api = "http://localhost:8000";
  const [selectedMenuItem, setSelectedMenuItem] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const provider = { api, selectedMenuItem, setSelectedMenuItem };

  return (
    <GlobalContext.Provider value={provider}>
      <Router>
        <Basetemplate>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route
              path="/models"
              element={<div className="mt-8"> Models </div>}
            />
            <Route path="/zerodha" element={<Zerodha />} />
            <Route path="/marketdata" element={<MarketData />} />
          </Routes>
        </Basetemplate>
      </Router>
    </GlobalContext.Provider>
  );
}

export default App;
