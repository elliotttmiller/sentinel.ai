import { CopilotRuntime, GoogleGenerativeAIAdapter } from "@copilotkit/runtime";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.REACT_APP_GOOGLE_API_KEY);
const copilotKit = new CopilotRuntime();

export const googleAdapter = new GoogleGenerativeAIAdapter({
  model: "gemini-1.5-pro",
  apiKey: process.env.REACT_APP_GOOGLE_API_KEY
});

// Example usage:
// copilotKit.useAdapter(googleAdapter);
