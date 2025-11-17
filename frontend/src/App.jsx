import { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Basetemplate from "./templates/Basetemplate";
import GlobalContext from "./templates/GlobalContext";
import MarketData from "./pages/MarketData";
import Portfolio from "./pages/portfolio/Portfolio";

function App() {
  const api = "http://localhost:8000";
  const [selectedMenuItem, setSelectedMenuItem] = useState("");
  const [profile, setProfile] = useState({
    user_id: "",
    user_name: "",
    email: "",
    user_shortname: "",
  });
  const [loggedIn, setLoggedIn] = useState(false);
  const provider = { api, selectedMenuItem, setSelectedMenuItem, profile };

  useEffect(() => {
    // Fetch user profile on app load
    fetch(`${api}/portfolio/profile`)
      .then((response) => response.json())
      .then((data) => {
        setProfile(data["data"]);
        setLoggedIn(true);
      });
  }, []);

  return (
    <GlobalContext.Provider value={provider}>
      <Router>
        <Basetemplate>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/marketdata" element={<MarketData />} />
          </Routes>
        </Basetemplate>
      </Router>
    </GlobalContext.Provider>
  );
}

export default App;
