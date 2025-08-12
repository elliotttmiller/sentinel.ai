import React from "react";
import { CopilotChat } from "@copilotkit/react-chat";

function CopilotMissionChat({ missionId }) {
  return (
    <div style={{ margin: "2rem 0" }}>
      <h3>Mission Chat</h3>
      <CopilotChat
        backendUrl={`/api/llm/chat?mission_id=${missionId}`}
        title={`Mission #${missionId} Chat`}
        placeholder="Discuss this mission..."
        theme="auto"
      />
    </div>
  );
}

export default CopilotMissionChat;
