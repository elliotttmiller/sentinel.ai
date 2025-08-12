
// Utility for LLM chat/agent calls via backend
export async function sendLLMChat(message, context = {}) {
  const baseUrl = process.env.REACT_APP_API_URL || "https://sentinelai-production.up.railway.app/api";
  const response = await fetch(baseUrl + "/llm/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, ...context }),
  });
  if (!response.ok) throw new Error("LLM chat failed");
  return response.json();
}

export async function sendLLMAgentAction(action, context = {}) {
  const baseUrl = process.env.REACT_APP_API_URL || "https://sentinelai-production.up.railway.app/api";
  const response = await fetch(baseUrl + "/llm/agent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, ...context }),
  });
  if (!response.ok) throw new Error("LLM agent action failed");
  return response.json();
}
