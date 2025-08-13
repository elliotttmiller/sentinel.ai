// Utility to send messages to CopilotKit backend in required format
export async function sendCopilotKitMessage(messages) {
  // Block and log any GraphQL-style payloads
  if (messages && typeof messages === 'object' && !Array.isArray(messages) && messages.query && messages.operationName) {
    console.error("CopilotKit: Attempted to send GraphQL payload to /copilotkit. This is not allowed.", messages);
    throw new Error("Cannot send GraphQL payload to CopilotKit endpoint. Use the correct GraphQL endpoint.");
  }
  // Guard against empty or malformed payloads
  if (!Array.isArray(messages) || messages.length === 0) {
    console.error("CopilotKit: Attempted to send empty or invalid messages array.", messages);
    throw new Error("Cannot send empty messages array to CopilotKit");
  }
  // Ensure messages is an array of objects with a 'text' field
  const formattedMessages = messages.map(msg => (typeof msg === 'string' ? { text: msg } : msg));
  const payload = { messages: formattedMessages };
  console.log("CopilotKit: Sending payload", payload);
  const response = await fetch("/copilotkit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorText = await response.text();
    console.error("CopilotKit request failed:", errorText);
    throw new Error("CopilotKit request failed: " + errorText);
  }
  return response.json();
}
