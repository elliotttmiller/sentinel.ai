
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import ThemeProvider from "./components/ThemeProvider";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
import { SentinelProvider } from "./context/SentinelContext";
import { CopilotKit } from "@copilotkit/react-core";

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <SentinelProvider>
        <ThemeProvider>
          <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <CopilotKit
              runtimeUrl="http://127.0.0.1:8000/api/copilotkit"
              publicApiKey={process.env.REACT_APP_PUBLIC_API_KEY}
            >
              <App />
            </CopilotKit>
          </BrowserRouter>
        </ThemeProvider>
      </SentinelProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
