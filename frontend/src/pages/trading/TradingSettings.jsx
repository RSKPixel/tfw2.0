import React from "react";

const TradingSettings = () => {
  const markets = ["Stocks", "Indices", "Metals", "Energy"];
  return (
    <div className="w-full flex flex-col">
      <div className="flex w-full rounded-t-xl bg-text-secondary/20 border border-text-secondary px-4 py-1">
        <span className="font-bold">Trading Settings</span>
      </div>

      <div className="flex flex-col items-center w-full gap-4 rounded-b-xl border border-text-secondary px-6 py-6">
        <div className="flex flex-row items-center w-full gap-4">
          {markets.map((market) => (
            <>
              <label className={`flex  gap-2 text-gray-400 ${market === "Forex" ? " opacity-50" : ""}`}>
                <input type="checkbox" className="accent-blue-500" />
              </label>
              <span className="font-bold">{market}</span>
            </>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TradingSettings;
