import React from "react";

const Basetemplate = ({ children }) => {
  return (
    <div className="flex flex-col h-screen">
      <header className="p-2 bg-zinc-950 shadow-md ">
        <span className="font-bold">Traders Framework</span>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="p-2 bg-zinc-950">
        <span className="text-sm">© 2025 TFW 2.0</span>
      </footer>
    </div>
  );
};

export default Basetemplate;
