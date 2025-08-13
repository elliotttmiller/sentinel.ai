import React from "react";
import { SearchIcon } from "lucide-react";
// import your cloud link component or use a placeholder
// import { LinkToCopilotCloud } from "./LinkToCopilotCloud";

export function TopBar() {
  return (
    <div className="p-2 h-[70px] hidden lg:block absolute w-full">
      <div className="flex justify-end items-center gap-2">
        {/* <LinkToCopilotCloud /> */}
        <SearchToggle />
      </div>
    </div>
  );
}

function SearchToggle() {
  const toggleSearch = () => {
    const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
    document.dispatchEvent(
      new KeyboardEvent("keydown", {
        key: "k",
        metaKey: isMac,
        ctrlKey: !isMac,
        bubbles: true,
      })
    );
  };
  return (
    <div onClick={toggleSearch} className="cursor-pointer h-12 px-4 w-[240px] xl:w-[275px] inline-flex items-center gap-2 border bg-gray-800 p-1.5 text-sm text-gray-400 transition-colors hover:bg-indigo-600 hover:text-white rounded-md max-md:hidden">
      <SearchIcon className="w-4 h-4 text-foreground" />
      Search docs
      <div className="ms-auto inline-flex gap-0.5">
        <kbd className="rounded-md border bg-gray-900 px-1.5">{navigator.platform.includes("Mac") ? "⌘" : "Ctrl"}</kbd>
        <kbd className="rounded-md border bg-gray-900 px-1.5">K</kbd>
      </div>
    </div>
  );
}
