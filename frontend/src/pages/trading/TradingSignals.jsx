import React from "react";

const TradingSignals = ({ signals }) => {
  return (
    <div className="w-full flex flex-col">
      <div className="flex w-full rounded-t-xl bg-text-secondary/20 border border-text-secondary px-4 py-1">
        <span className="font-bold">Signals</span>
      </div>

      <div className="flex flex-col items-center w-full gap-4 rounded-b-xl border border-text-secondary px-6 py-6">
        {/* model, signal, symbol, setup candle, entry_price */}

        <div className="w-full overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="border-b border-text-secondary/40">
                <th className="text-left px-4 py-2">Model</th>
                <th className="text-left px-4 py-2">Signal</th>
                <th className="text-left px-4 py-2">Symbol</th>
                <th className="text-left px-4 py-2">Setup Candle</th>
                <th className="text-left px-4 py-2">Entry Price</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal, index) => (
                <tr
                  key={index}
                  className={
                    index % 2 === 0
                      ? "bg-text-secondary/10"
                      : "bg-text-secondary/5"
                  }
                >
                  <td className="px-4 py-2">{signal.model}</td>
                  <td className="px-4 py-2">{signal.signal}</td>
                  <td className="px-4 py-2">{signal.symbol}</td>
                  <td className="px-4 py-2">
                    {new Date(signal.setup_candle).toLocaleString()}
                  </td>
                  <td className="px-4 py-2">{signal.entry_price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TradingSignals;
