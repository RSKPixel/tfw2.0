import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../../templates/GlobalContext";
import TradingModels from "./TradingModels";
import TradingSettings from "./TradingSettings";
import Spinner from "../../components/Spinner";
import TradingSignals from "./TradingSignals";

const Trading = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [models, setModels] = useState([]);
  const [selectedMarkets, setSelectedMarkets] = useState(["NFO", "MCX"]);
  const [selectedTimeframe, setSelectedTimeframe] = useState("1d");
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFetchSignals = () => {
    setLoading(true);
    fetch(`${api}/signals/trading-signals2/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        models: models,
        markets: selectedMarkets,
        timeframe: selectedTimeframe,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        data = data.data;
        setSignals(data.signals);
        console.log("Fetched trading signals:", data.signals);
        setLoading(false);
      })
      .catch((error) => {
        console.error(
          "An error occurred while fetching trading signals. Please try again.",
          error
        );

        setLoading(false);
      });
  };

  useEffect(() => {
    setSelectedMenuItem("Trading");
  }, []);

  return (
    <div className="mt-2 px-4 py-8 flex flex-col gap-4">
      <div className=" flex flex-row gap-4">
        <TradingModels setModels={setModels} />
        <TradingSettings
          selectedMarkets={selectedMarkets}
          selectedTimeframe={selectedTimeframe}
          setSelectedMarkets={setSelectedMarkets}
          setSelectedTimeframe={setSelectedTimeframe}
        />
      </div>
      <button disabled={loading} onClick={handleFetchSignals}>
        Fetch Signals <Spinner loading={loading} />
      </button>
      <TradingSignals signals={signals} />
    </div>
  );
};

export default Trading;
