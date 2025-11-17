import React, { useContext, useEffect } from "react";
import GlobalContext from "../templates/GlobalContext";

const Dashboard = () => {
  const { api, setSelectedMenuItem } = useContext(GlobalContext);

  useEffect(() => {
    setSelectedMenuItem("Dashboard");
  }, []);

  return (
    <div className="flex flex-row gap-4 justify-center border-secondary p-8 h-full overflow-hidden">
      <div className="border w-[22%] p-4 rounded-md flex flex-col gap-4 border-secondary h-full overflow-y-auto"></div>
      <div className="w-[78%] p-1 border border-secondary rounded-md h-full overflow-y-hidden">
        Dashboard
      </div>
    </div>
  );
};

export default Dashboard;
