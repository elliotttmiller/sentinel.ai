import React, { createContext, useContext } from "react";
import { useLocalStorage } from "usehooks-ts";

const TailoredContentContext = createContext();

export function TailoredContentProvider({ children }) {
  const [mode, setMode] = useLocalStorage("copilotkit-tailored-content", "default");
  return (
    <TailoredContentContext.Provider value={{ mode, setMode }}>
      {children}
    </TailoredContentContext.Provider>
  );
}

export function useTailoredContent(options = ["default"], defaultOption = "default") {
  const context = useContext(TailoredContentContext);
  if (!context) throw new Error("useTailoredContent must be used within a TailoredContentProvider");
  React.useEffect(() => {
    if (!options.includes(context.mode)) {
      context.setMode(defaultOption);
    }
  }, [context.mode]);
  return context;
}
