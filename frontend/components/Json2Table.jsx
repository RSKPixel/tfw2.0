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
    <div className="p-2 bg-bg-primary rounded-2xl">
      <div className="overflow-y-auto max-h-[85vh] rounded-t-2xl">
        <table className="w-full border-0  border-secondary">
          <thead className="bg-zinc-800 border sticky top-0 z-20 border-secondary">
            <tr>
              {keys.map((key) => (
                <th
                  key={key}
                  className={`py-1 px-4 border border-secondary  ${
                    formatting[key]?.type === "numeral" ? "text-right" : ""
                  }`}
                >
                  {formatting[key]?.label || key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {jsonData.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-secondary/40">
                {keys.map((key) => (
                  <td
                    key={key}
                    className={`py-1 px-4 border border-secondary ${
                      formatting[key]?.type === "numeral"
                        ? "text-right"
                        : "text-center"
                    }`}
                  >
                    {formatValue(key, row[key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {/* <div className="absolute top-[calc(var(--header-height,4rem))] left-0 right-0 h-1 bg-primary z-30 pointer-events-none"></div> */}
      </div>
    </div>
  );
};

export default Json2Table;
