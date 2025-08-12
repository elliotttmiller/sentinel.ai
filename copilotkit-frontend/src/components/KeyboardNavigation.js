import { useEffect } from "react";
import { useSentinel } from "../context/SentinelContext";

export default function KeyboardNavigation() {
  const { state, dispatch } = useSentinel();
  useEffect(() => {
    function handleKeyDown(e) {
      // ESC closes modals
      if (e.key === "Escape") {
        if (state.showMissionModal) dispatch({ type: "CLOSE_MISSION_MODAL" });
        if (state.showEventModal) dispatch({ type: "CLOSE_EVENT_MODAL" });
      }
      // Ctrl+M opens first mission modal
      if ((e.ctrlKey || e.metaKey) && e.key === "m" && !e.shiftKey) {
        if (state.missions.length > 0 && !state.showMissionModal) {
          dispatch({ type: "OPEN_MISSION_MODAL", mission: state.missions[0] });
        }
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [state, dispatch]);
  return null;
}
