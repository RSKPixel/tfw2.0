import React from "react";

const Basetemplate = ({ children }) => {
  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* Fixed Header */}
      <header className="p-2 bg-primary border-b border-secondary fixed top-0 left-0 right-0 z-10">
        <span className="font-bold">Traders Framework</span>
      </header>

      {/* Scrollable Main */}
      <main className="flex-1 bg-primary overflow-y-auto mt-5 mb-5">
        {children}
      </main>

      {/* Fixed Footer */}
      <footer className="p-2 bg-primary border-t border-secondary fixed bottom-0 left-0 right-0 z-10">
        <span className="text-sm">© 2025 TFW 2.0</span>
      </footer>
    </div>
  );
};

export default Basetemplate;
