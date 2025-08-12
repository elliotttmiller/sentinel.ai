import React from "react";


import MissionList from "../components/MissionList";
import MissionModal from "../components/MissionModal";

function Missions() {
  return (
    <div>
      <h1>Missions</h1>
      <MissionList />
      <MissionModal />
    </div>
  );
}

export default Missions;
