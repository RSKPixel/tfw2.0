import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../../templates/GlobalContext";

const TradingModels = ({ setModels }) => {
  const { api } = useContext(GlobalContext);
  const [tradingModels, setTradingModels] = useState({});
  const [selectedModels, setSelectedModels] = useState([]);

  const allKeys = Object.keys(tradingModels);

  useEffect(() => {
    fetchTradingModels();
  }, []);

  const toggleModel = (code) => {
    setSelectedModels((prev) => {
      const next = prev.includes(code)
        ? prev.filter((m) => m !== code)
        : [...prev, code];

      setModels(next);
      return next;
    });
  };

  const toggleAll = () => {
    setSelectedModels((prev) => {
      const next = prev.length === allKeys.length ? [] : allKeys;
      setModels(next);
      return next;
    });
  };

  const fetchTradingModels = () => {
    fetch(`${api}/signals/trading-models/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.status === "success") {
          setTradingModels(data.data);
          const keys = Object.keys(data.data);
          setSelectedModels(keys);
          setModels(keys);
        }
      });
  };

  return (
    <div className="w-full flex flex-col">
      <div className="flex w-full rounded-t-xl bg-text-secondary/20 border border-text-secondary px-4 py-1">
        <span className="font-bold">Trading Models</span>
        <input
          type="checkbox"
          className="accent-blue-500 ml-auto"
          checked={
            allKeys.length > 0 && selectedModels.length === allKeys.length
          }
          onChange={toggleAll}
        />
      </div>

      <div className="flex flex-col items-center w-full gap-4 rounded-b-xl border border-text-secondary px-6 py-6">
        <ul className="flex gap-4">
          {Object.entries(tradingModels).map(([code, label]) => (
            <li key={code}>
              <label className="flex items-center gap-2" htmlFor={code}>
                <input
                  id={code}
                  type="checkbox"
                  className="accent-blue-500"
                  checked={selectedModels.includes(code)}
                  onChange={() => toggleModel(code)}
                />
                {label}
              </label>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TradingModels;
