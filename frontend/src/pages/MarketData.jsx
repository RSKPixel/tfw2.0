import React, { useContext, useEffect, useState } from "react";
import GlobalContext from "../templates/GlobalContext";
import Loader from "../components/Loader";
import Spinner from "../components/Spinner";

const MarketData = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSelectedMenuItem("Market Data");
  }, []);

  const handleDownloadData = () => {
    setLoading(true);
    setMessage("");
    fetch(`${api}/data/fetch-save-eod`, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message);
        setLoading(false);
      });
  };

  return (
    <div className="mt-2 px-4 py-8">
      <div className="w-full flex flex-col">
        <div className="flex flex-row w-full rounded-t-xl bg-text-secondary/20 border-text-secondary border px-4 py-1">
          <span className="font-bold">Market Data Grabber</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-xl bg-primary border-text-secondary border-b border-s border-e px-6 py-6">
          <button disabled={loading} onClick={handleDownloadData}>
            Download Data <Spinner loading={loading} />
          </button>
          {message && <div className="ms-4 text-stone-200 p-2">{message}</div>}
        </div>
      </div>
    </div>
  );
};

export default MarketData;
