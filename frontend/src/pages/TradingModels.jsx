import React, { use, useContext, useEffect, useState } from "react";
import GlobalContext from "../templates/GlobalContext";

const TradingModels = ({ setModels }) => {
  const { api } = useContext(GlobalContext);
  const [tradingModels, setTradingModels] = React.useState([]);
  const [selectedModels, setSelectedModels] = useState([]);

  useEffect(() => {
    fetchTradingModels();
  }, []);

  const toggleModel = (code) => {
    setSelectedModels((prev) => (prev.includes(code) ? prev.filter((m) => m !== code) : [...prev, code]));
    setModels((prev) => (prev.includes(code) ? prev.filter((m) => m !== code) : [...prev, code]));
  };

  const toggleAll = () => {
    setSelectedModels(selectedModels.length === allKeys.length ? [] : allKeys);
  };
  const fetchTradingModels = () => {
    fetch(`${api}/signals/trading-models/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          setTradingModels(data.data);
          setSelectedModels(Object.keys(data.data));
          setModels(Object.keys(data.data));
        } else {
          console.error("Failed to fetch trading models");
        }
      })
      .catch((error) => {
        console.error("An error occurred while fetching trading models: ", error);
      });
  };

  return (
    <div className="w-full flex flex-col">
      <div className="flex flex-row w-full rounded-t-xl bg-text-secondary/20 border-text-secondary border px-4 py-1">
        <span className="font-bold">Trading Models</span>
      </div>

      <div className="flex flex-col w-full items-center gap-4 rounded-b-xl bg-primary border-text-secondary border-b border-s border-e px-6 py-6">
        {tradingModels && (
          <ul className="flex flex-row gap-4">
            {Object.entries(tradingModels).map(([code, label]) => (
              <li key={code} className="flex items-center gap-2">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="accent-blue-500" checked={selectedModels.includes(code)} onChange={() => toggleModel(code)} />
                  <span>{label}</span>
                </label>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default TradingModels;
