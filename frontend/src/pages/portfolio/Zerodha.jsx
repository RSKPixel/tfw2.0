import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../../templates/GlobalContext";
import Loader from "../../components/Loader";

const Zerodha = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setSelectedMenuItem("Portfolio (Zerodha)");
  }, []);

  return (
    <div className="grid sm:grid-cols-1 lg:grid-cols-3 gap-8 mt-2 px-4 py-8">
      {loading && (
        <Loader message={"Downloading EOD Date for NFO / MCX / CDS . . ."} />
      )}
      <div className="w-full flex flex-col">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Open Positions</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>

      <div className="w-full flex flex-col lg:col-span-2">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Equity Curve</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>

      <div className="w-full flex flex-col">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Margin</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>

      <div className="w-full flex flex-col">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Orders</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>

      <div className="w-full flex flex-col">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Funds</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>
    </div>
  );
};

export default Zerodha;
