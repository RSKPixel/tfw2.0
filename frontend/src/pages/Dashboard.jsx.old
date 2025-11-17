import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../templates/GlobalContext";
import Json2Table from "../components/Json2Table";
import Pills from "../components/Pills";

const Dashboard = () => {
  const { api } = useContext(GlobalContext);
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState([]);
  const [data, setData] = useState(null);
  const [taData, setTaData] = useState(true);

  useEffect(() => {
    fetch(`${api}/symbols`)
      .then((response) => response.json())
      .then((data) => setSymbols(data))
      .catch((error) => console.error("Error fetching symbols:", error));
  }, []);

  const handleSelection = (event) => {
    const options = event.target.options;
    const selected = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        selected.push(options[i].value);
      }
    }
    setSelectedSymbol(selected[0]);
  };

  useEffect(() => {
    const endpoint = taData ? "ohlcv-ta" : "ohlcv";

    fetch(`${api}/${endpoint}?symbol=${selectedSymbol}`)
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching OHLCV data:", error));
  }, [selectedSymbol, taData]);
  return (
    <div className="flex flex-row gap-4 justify-center border-secondary p-8 h-full overflow-hidden">
      {/* Left side */}
      <div className="border w-[22%] p-4 rounded-md flex flex-col gap-4 border-secondary h-full overflow-y-auto">
        <div className="flex flex-col w-full gap-2">
          <label className="mr-2">Select Symbol:</label>
          <select
            multiple={true}
            onChange={handleSelection}
            className="border px-2 py-2 h-64 focus:ring-0 focus:outline-none rounded-md bg-bg-primary border-secondary text-text-primary w-full"
          >
            {symbols.map((symbol) => (
              <option className="p-2" key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-row w-full items-center justify-center">
          <Pills
            title={"Timeframes"}
            items={["5mins", "15mins", "60mins", "1Day"]}
            multiple={false}
            selected={selectedTimeframe}
            setSelected={setSelectedTimeframe}
          />
        </div>
        {/* Add other widgets here — all scroll within the same fixed-height box */}
      </div>

      {/* Right side */}
      <div className="w-[78%] p-1 border border-secondary rounded-md h-full overflow-y-hidden">
        <Json2Table
          jsonData={data}
          formatting={{
            date: { label: "Date", type: "date", format: "DD-MM-YYYY HH:mm" },
            open: { label: "Open", type: "numeral", format: "0,0.00" },
            high: { label: "High", type: "numeral", format: "0,0.00" },
            low: { label: "Low", type: "numeral", format: "0,0.00" },
            close: { label: "Close", type: "numeral", format: "0,0.00" },
            volume: { label: "Volume", type: "numeral", format: "0,0" },
            swing_high: {
              label: "Swing High",
              type: "boolean",
              format: "True",
            },
            swing_low: {
              label: "Swing Low",
              type: "boolean",
              format: "True",
            },
          }}
        />
      </div>
    </div>
  );
};

export default Dashboard;
