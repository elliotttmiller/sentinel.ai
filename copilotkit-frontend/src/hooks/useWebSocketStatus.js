import { useEffect, useState } from "react";

export function useWebSocketStatus(url = "ws://localhost:8000/ws/status") {
  const [status, setStatus] = useState("");

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      setStatus(event.data);
    };
    ws.onerror = (err) => {
      setStatus("WebSocket error");
    };
    ws.onclose = () => {
      setStatus("WebSocket closed");
    };
    return () => ws.close();
  }, [url]);

  return status;
}
