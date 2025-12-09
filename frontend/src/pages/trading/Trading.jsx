import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../../templates/GlobalContext";
import TradingModels from "./TradingModels";
import TradingSettings from "./TradingSettings";

const Trading = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [models, setModels] = useState([]);

  useEffect(() => {
    setSelectedMenuItem("Trading");
  }, []);

  return (
    <div className="mt-2 px-4 py-8 flex flex-col gap-8">
      <TradingModels setModels={setModels} />
      <TradingSettings />
    </div>
  );
};

export default Trading;
