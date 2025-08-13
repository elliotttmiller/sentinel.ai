import React from "react";
// You can replace this with your own Banner component or use a simple div
export function AGUIBanner() {
  return (
    <div className="w-full text-white bg-indigo-500 dark:bg-indigo-900 py-4 px-2 rounded-md mb-4">
      <p className="w-3/4">
        We're officially launching AG-UI, the protocol for agent and user interactivity! <a href="https://ag-ui.com" target="_blank" rel="noopener noreferrer" className="underline">Learn more</a>.
      </p>
    </div>
  );
}
