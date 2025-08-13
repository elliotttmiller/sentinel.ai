import React, { useEffect, useState } from "react";
import { useSentinel } from "../context/SentinelContext";

function MissionList() {
  const { state, dispatch } = useSentinel();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/missions")
      .then((res) => res.json())
      .then((data) => {
        dispatch({ type: "SET_MISSIONS", missions: data.missions });
        setLoading(false);
      });
     
  }, [dispatch]);

  if (loading) return <div>Loading missions...</div>;

  return (
    <div>
      <h2>Active Missions</h2>
      <ul>
        {state.missions.map((mission) => (
          <li
            key={mission.id}
            style={{ cursor: "pointer" }}
            onClick={() => dispatch({ type: "OPEN_MISSION_MODAL", mission })}
          >
            {mission.name} - {mission.status}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MissionList;
