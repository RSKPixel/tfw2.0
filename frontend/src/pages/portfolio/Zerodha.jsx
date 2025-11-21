import React, { createRef, useContext, useEffect, useState } from "react";
import GlobalContext from "../../templates/GlobalContext";
import Loader from "../../components/Loader";
import numeral from "numeral";
import moment from "moment";
import Spinner from "../../components/Spinner";

numeral.defaultFormat("0,0.00");

const Zerodha = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);
  const [loading, setLoading] = useState(false);
  const [loaderMessage, setLoaderMessage] = useState("");
  const [profile, setProfile] = useState(null);
  const [zerodhaConnection, setZerodhaConnection] = useState(false);

  useEffect(() => {
    setSelectedMenuItem("Portfolio (Zerodha)");
    fetch(`${api}/zerodha/profile/`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data["status"] === "success") {
          setProfile(data["data"]);
          setZerodhaConnection(true);
        } else {
          setZerodhaConnection(false);
          setProfile(null);
        }
      });
  }, []);

  return (
    <div className="grid sm:grid-cols-1 lg:grid-cols-5 gap-8 mt-2 px-4 py-8">
      {/* {loading && <Loader message={loaderMessage} />} */}

      <Positions
        colspan={2}
        profile={profile}
        setLoaderMessage={setLoaderMessage}
        zerodhaConnection={zerodhaConnection}
        setLoading={setLoading}
      />

      <EquityCurve
        colspan={3}
        profile={profile}
        setLoaderMessage={setLoaderMessage}
        setLoading={setLoading}
      />

      <TradeBook
        colspan={2}
        profile={profile}
        zerodhaConnection={zerodhaConnection}
        setLoaderMessage={setLoaderMessage}
        setLoading={setLoading}
      />

      <div className="w-full flex flex-col lg:col-span-3">
        <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
          <span className="font-bold">Models</span>
        </div>
        <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
      </div>
    </div>
  );
};

const EquityCurve = ({ colspan, profile, setLoaderMessage, setLoading }) => {
  const { api } = useContext(GlobalContext);
  const [localLoading, setLocalLoading] = useState(false);
  const period = ["1Y", "3Y", "5Y", "All"];
  const timeframe = ["Daily", "Weekly", "Montly"];
  const [selectedPeriod, setSelectedPeriod] = useState("All");
  const [selectedTimeframe, setSelectedTimeframe] = useState("Daily");

  return (
    <div className={`w-full flex flex-col lg:col-span-3`}>
      <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
        <span className="font-bold me-5">
          Equity Curve (
          {timeframe.map((tf, index) => (
            <>
              {index > 0 && <span className={`${index > 0 && "ms-2"}`}>|</span>}
              <span
                key={index}
                className={`font-bold ms-2 ${
                  index == timeframe.length - 1 && "me-2"
                } cursor-pointer hover:underline underline-offset-4 ${
                  selectedTimeframe === tf ? "underline" : ""
                }`}
                onClick={() => setSelectedTimeframe(tf)}
              >
                {tf}
              </span>
            </>
          ))}
          )
        </span>
        <span className="ms-auto flex flex-row">
          {period.map((p, index) => (
            <span
              key={index}
              className={`font-bold ms-auto me-2 cursor-pointer hover:underline underline-offset-4 ${
                selectedPeriod === p ? "underline" : ""
              }`}
              onClick={() => setSelectedPeriod(p)}
            >
              {p}
            </span>
          ))}
        </span>
      </div>
      <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6"></div>
    </div>
  );
};

const Positions = ({
  profile,
  zerodhaConnection,
  setLoaderMessage,
  setLoading,
  colspan,
}) => {
  const { api } = useContext(GlobalContext);
  const [openPositions, setOpenPositions] = useState([]);
  const [localLoading, setLocalLoading] = useState(false);

  useEffect(() => {
    setLocalLoading(true);
    fetch(`${api}/zerodha/positions/`, {
      method: "POST",
      body: JSON.stringify({ user_id: profile?.user_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        setOpenPositions(data["data"]["net"]);
        setLocalLoading(false);
      });
  }, [profile]);

  return (
    <div className={`w-full flex flex-col lg:col-span-2`}>
      <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
        <span className="font-bold">Open Positions</span>
        <span className="font-bold ms-auto">
          {profile && zerodhaConnection
            ? `${String(profile?.user_shortname).toUpperCase()} (${
                profile?.user_id
              })`
            : "N/A"}
        </span>
      </div>
      <div className="flex flex-col w-full items-center gap-4 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-6 py-6">
        {openPositions.length === 0 && (
          <span className=" text-text-secondary">
            No open positions available.
          </span>
        )}
      </div>
    </div>
  );
};

const TradeBook = ({ profile, setLoaderMessage, setLoading, colspan }) => {
  const { api } = useContext(GlobalContext);
  const tbFileDialog = createRef();
  const [localLoading, setLocalLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    setLocalLoading(true);
    fetch(`${api}/zerodha/tradebook?user_id=${profile?.user_id}`)
      .then((response) => response.json())
      .then((data) => {
        setTrades(data["data"]);
        setLocalLoading(false);
      });
  }, [profile]);

  const handleTradeBookUpload = (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    setLoading(true);
    setMessage("");
    setLoaderMessage("Uploading trade book...");

    formData.append("file", file);
    formData.append("user_id", profile.user_id);
    formData.append("broker", "Zerodha");

    fetch(`${api}/zerodha/tradebook-upload`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message);
        setLoaderMessage("");
        setLoading(false);
      })
      .finally((error) => {
        setMessage("Error uploading trade book. Please try again.");
        setLoaderMessage("");
        setLoading(false);
        setLocalLoading(false);
      });
  };
  return (
    <div className={`w-full flex flex-col lg:col-span-2`}>
      <div className="flex flex-row w-full rounded-t-lg bg-text-secondary/20 border-text-secondary border px-2 py-1">
        <span className="font-bold">Trade Book</span>
        <span className="font-bold ms-auto cursor-pointer">
          <i
            className="bi bi-upload"
            onClick={() => tbFileDialog.current.click()}
          ></i>
          <input
            ref={tbFileDialog}
            type="file"
            accept=".csv"
            onChange={handleTradeBookUpload}
            className="hidden"
          />
        </span>
      </div>
      <div className="flex flex-col w-full items-center gap-0 rounded-b-lg bg-primary border-text-secondary border-b border-s border-e px-0 pt-0 min-h-12">
        <Spinner loading={localLoading} className="mt-2" />
        {trades.length > 0 &&
          trades.map((trade, index) => (
            <div
              key={index}
              className="grid grid-cols-[3fr_1fr_1fr_1fr_1fr] w-full hover:bg-text-secondary/20 px-2 py-2 border-secondary border-t cursor-pointer"
            >
              <div className="text-start flex flex-col">
                <span>{trade.symbol}</span>
                <span className="text-xs flex flex-row gap-1">
                  {moment(trade.expiry_date).format("DD-MM-YYYY")}
                </span>
              </div>
              <span>
                {trade.exchange} ({trade.segment})
              </span>
              <div className="text-end">
                {moment(trade.trade_date).format("DD-MM-YYYY")}
              </div>
              <div className="text-end">
                {numeral(trade.quantity).format("0.00")}
              </div>
              <div className="text-end">
                {numeral(trade.price).format("0,0.00")}
              </div>
            </div>
          ))}
        {message && (
          <span className="text-sm pt-2 pb-2 border-t border-secondary w-full text-center text-text-secondary">
            {message}
          </span>
        )}
      </div>
    </div>
  );
};

export default Zerodha;
