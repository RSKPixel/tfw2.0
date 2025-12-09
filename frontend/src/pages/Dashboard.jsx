import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../templates/GlobalContext";
import TradingModels from "./TradingModels";

const Dashboard = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [models, setModels] = useState([]);

  useEffect(() => {
    setSelectedMenuItem("Dashboard");
  }, []);

  return (
    <div className="mt-2 px-4 py-8">
      <TradingModels setModels={setModels} />
    </div>
  );
};

export default Dashboard;
