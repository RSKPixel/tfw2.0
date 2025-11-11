import { useState } from "react";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Basetemplate from "./templates/Basetemplate";
import GlobalContext from "./templates/GlobalContext";

function App() {
  const api = "http://localhost:8000";
  const provider = { api };

  return (
    <GlobalContext.Provider value={provider}>
      <Basetemplate>
        <Dashboard />
      </Basetemplate>
    </GlobalContext.Provider>
  );
}

export default App;
