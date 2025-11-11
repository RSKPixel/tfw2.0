import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../templates/GlobalContext";
import Json2Table from "../../components/Json2Table";

const Dashboard = () => {
  const { api } = useContext(GlobalContext);
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [data, setData] = useState(null);

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
    fetch(`${api}/ohlcv?symbol=${selectedSymbol}`)
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching OHLCV data:", error));
  }, [selectedSymbol]);

  return (
    <div className="flex flex-row w-full h-full flex-1">
      <div className="flex h-full flex-col gap-4 w-1/8 shadow-lg border-r border-zinc-700">
        <select multiple="2" onChange={handleSelection}>
          {symbols.map((symbol) => (
            <option key={symbol} value={symbol}>
              {symbol}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 border-zinc-700 p-2">
        <Json2Table
          jsonData={data}
          formatting={{
            date: { label: "Date", type: "date", format: "DD-MM-YYYY HH:mm" },
            open: { label: "Open", type: "numeral", format: "0,0.00" },
            high: { label: "High", type: "numeral", format: "0,0.00" },
            low: { label: "Low", type: "numeral", format: "0,0.00" },
            close: { label: "Close", type: "numeral", format: "0,0.00" },
            volume: { label: "Volume", type: "numeral", format: "0,0" },
          }}
        />
      </div>
    </div>
  );
};

export default Dashboard;
