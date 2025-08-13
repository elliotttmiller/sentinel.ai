import { useEffect, useRef } from "react";
import { useSentinel } from "../context/SentinelContext";

export function useRealtime() {
  const { dispatch } = useSentinel();
  const wsRef = useRef(null);

  useEffect(() => {
    let ws;
    function connect() {
      const apiUrl = process.env.REACT_APP_API_URL.replace(/^http/, "ws");
      ws = new window.WebSocket(apiUrl + "/ws");
      wsRef.current = ws;
      ws.onopen = () => {
        // Optionally dispatch connection state
        // dispatch({ type: "WS_CONNECTED" });
      };
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Dispatch updates based on event type
        if (data.type === "missions") {
          dispatch({ type: "SET_MISSIONS", missions: data.missions });
        }
        if (data.type === "agent_activity") {
          dispatch({ type: "SET_AGENT_ACTIVITY", agentActivity: data.activity });
        }
        // ...handle more event types as needed
      };
      ws.onclose = () => {
        setTimeout(connect, 3000); // Reconnect after 3s
      };
      ws.onerror = () => {
        ws.close();
      };
    }
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [dispatch]);
}
