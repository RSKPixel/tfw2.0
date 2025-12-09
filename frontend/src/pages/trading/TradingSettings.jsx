import React, { useState } from "react";

const TradingSettings = ({
  selectedMarkets,
  setSelectedMarkets,
  selectedTimeframe,
  setSelectedTimeframe,
}) => {
  const markets = ["NFO", "MCX"];
  const timeframes = ["1d", "75m", "15m"];

  const handleMarkets = (market) => {
    setSelectedMarkets((prev) => {
      if (prev.includes(market)) {
        return prev.filter((m) => m !== market);
      } else {
        return [...prev, market];
      }
    });
  };

  const handleTF = (tf) => {
    setSelectedTimeframe(tf);
  };

  return (
    <div className="w-full flex flex-col">
      <div className="flex w-full rounded-t-xl bg-text-secondary/20 border border-text-secondary px-4 py-1">
        <span className="font-bold">Trading Settings</span>
      </div>

      <div className="flex flex-col items-center w-full rounded-b-xl border border-text-secondary px-6 py-6">
        <div className="flex flex-row  items-center align-middle w-fit gap-32">
          <ul className="flex gap-4">
            {markets.map((market) => (
              <li key={market}>
                <label className={`flex  gap-2 text-gray-400 `}>
                  <input
                    type="checkbox"
                    className="accent-blue-500"
                    checked={selectedMarkets.includes(market)}
                    onChange={() => handleMarkets(market)}
                  />
                  <span className="font-bold">{market}</span>
                </label>
              </li>
            ))}
          </ul>

          {/* <div className="ms-auto"></div> */}

          <ul className="flex gap-4">
            {timeframes.map((tf) => (
              <li key={tf}>
                <label className={`flex  gap-2 text-gray-400 `}>
                  <input
                    type="radio"
                    name="timeframe"
                    checked={selectedTimeframe === tf}
                    className="accent-blue-500"
                    onChange={() => handleTF(tf)}
                  />
                  <span className="font-bold">{tf}</span>
                </label>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TradingSettings;
