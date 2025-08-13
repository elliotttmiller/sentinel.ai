// Wraps CopilotKit messages to add required methods
export function wrapCopilotKitMessage(msg) {
  return {
    ...msg,
    isResultMessage: () => !!msg.isResultMessage,
    isAgentStateMessage: () => !!msg.isAgentStateMessage,
  };
}
