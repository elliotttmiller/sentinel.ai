// Utility for WebSocket real-time updates
export function connectWebSocket(path = "/api/ws", onMessage) {
  const ws = new WebSocket(`ws://localhost:8001${path}`);
  ws.onmessage = (event) => {
    if (onMessage) onMessage(JSON.parse(event.data));
  };
  return ws;
}
