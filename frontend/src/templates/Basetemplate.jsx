import React, { useContext } from "react";
import { Link } from "react-router-dom";
import GlobalContext from "./GlobalContext";

const Basetemplate = ({ children }) => {
  const { api, selectedMenuItem, profile } = useContext(GlobalContext);

  const menuItems = {
    Dashboard: "/",
    Portfolio: "/portfolio",
    "Market Data": "/marketdata",
  };
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Fixed Header */}
      <header className="flex flex-row items-center px-3 py-2 h-12 bg-primary border-b border-secondary fixed top-0 left-0 right-0 z-10">
        <span className="font-bold text-lg  cursor-pointer">
          Trader's Framework
        </span>
        <span className="ms-auto font-bold flex flex-row gap-4">
          {Object.entries(menuItems).map(([name, path]) => (
            <Link
              key={name}
              className={` ${
                selectedMenuItem === name
                  ? "text-text-secondary"
                  : "hover:text-yellow-400"
              }`}
              to={path}
            >
              {name}
            </Link>
          ))}
          <span className="border-l border-secondary ps-4">
            {String(profile?.user_shortname || "Guest").toUpperCase()} (
            {profile?.user_id || "-"})
          </span>
        </span>
      </header>

      {/* Scrollable Main */}
      <main className="flex-1 bg-primary overflow-y-auto mt-8 mb-0">
        {children}
      </main>
    </div>
  );
};

export default Basetemplate;
