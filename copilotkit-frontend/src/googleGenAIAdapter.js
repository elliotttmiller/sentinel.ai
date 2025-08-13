import { GoogleGenerativeAIAdapter } from "@copilotkit/runtime";


export const googleAdapter = new GoogleGenerativeAIAdapter({
  model: "gemini-1.5-pro", // Match backend model
  apiKey: process.env.REACT_APP_GOOGLE_API_KEY
});

// Example usage:
// copilotKit.useAdapter(googleAdapter);
