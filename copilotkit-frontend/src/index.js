
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import ThemeProvider from "./components/ThemeProvider";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
import { SentinelProvider } from "./context/SentinelContext";
import { CopilotProvider } from "@copilotkit/react-core";

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <SentinelProvider>
        <ThemeProvider>
          <BrowserRouter>
            <CopilotProvider
              runtimeUrl={process.env.REACT_APP_API_URL + "/copilotkit"}
              publicApiKey={process.env.REACT_APP_PUBLIC_API_KEY}
            >
              <App />
            </CopilotProvider>
          </BrowserRouter>
        </ThemeProvider>
      </SentinelProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
