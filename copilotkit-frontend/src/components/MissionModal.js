import React from "react";
import { useSentinel } from "../context/SentinelContext";

export default function MissionModal() {
  const { state, dispatch } = useSentinel();
  const mission = state.selectedMission;
  if (!state.showMissionModal || !mission) return null;
  return (
    <div className="modal mission-modal" tabIndex="-1" style={{ display: "block" }}>
      <div className="modal-content">
        <h2>Mission: {mission.name}</h2>
        <p>Status: {mission.status}</p>
        {/* Render mission events, details, controls here */}
        <button onClick={() => dispatch({ type: "CLOSE_MISSION_MODAL" })}>Close</button>
      </div>
    </div>
  );
}
