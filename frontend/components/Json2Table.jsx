import React, { useEffect } from "react";
import moment from "moment";
import numeral from "numeral";

const Json2Table = ({ jsonData, formatting = {} }) => {
  const keys = jsonData && Object.keys(jsonData[0] || {});

  if (!jsonData || jsonData.length === 0) {
    return;
  }

  const formatValue = (key, value) => {
    if (!formatting[key]) {
      return value;
    }
    if (formatting[key].type === "date") {
      return moment(value).format(formatting[key].format);
    }
    if (formatting[key].type === "numeral") {
      return numeral(value).format(formatting[key].format);
    }
    return value;
  };

  return (
    <div className="w-full flex-row">
      <div className="w-2/3 border h-64 overflow-auto border-zinc-700 mx-auto rounded-md">
        <table className="w-full rounded-md px-2 table-auto">
          <thead>
            <tr className="bg-zinc-800 sticky top-0">
              {keys.map((key) => (
                <th
                  key={key}
                  className={`py-1 px-4 border border-zinc-700 ${
                    formatting[key] &&
                    (formatting[key].type === "numeral" ? "text-right" : "")
                  }`}
                >
                  {formatting[key] ? formatting[key].label : key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {jsonData.map((row, rowIndex) => (
              <tr key={rowIndex} className="text-center hover:bg-zinc-800">
                {keys.map((key) => (
                  <td
                    key={key}
                    className={`py-1 px-4 border border-zinc-700 ${
                      formatting[key] &&
                      (formatting[key].type === "numeral" ? "text-right" : "")
                    }`}
                  >
                    {formatValue(key, row[key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Json2Table;
