import React from "react";

const Pills = ({
  title,
  items,
  setSelected,
  selected = [],
  multiple = false,
}) => {
  const styling = `border border-secondary cursor-pointer border-l-0 first:border-l last:border-r text-text-primary py-1.5 px-3 flex-1 text-center first:rounded-s-md last:rounded-e-md`;

  const handleSelection = (selectedItem) => {
    if (!multiple) {
      setSelected([selectedItem]);
      return;
    }

    if (selected.find((sel) => sel === selectedItem)) {
      const newSelection = selected.filter((sel) => sel !== selectedItem);
      setSelected(newSelection);
    } else {
      setSelected([...selected, selectedItem]);
    }
  };

  return (
    <div className="flex flex-col w-full gap-2">
      <span>{title}</span>
      <div className="flex flex-wrap w-full">
        {items.map((item, index) => (
          <span
            key={index}
            onClick={() => handleSelection(item)}
            className={`${styling} ${
              selected.find((sel) => sel === item)
                ? "bg-text-secondary/90 hover:bg-text-secondary"
                : "bg-bg-primary hover:bg-secondary/40"
            }`}
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
};

export default Pills;
