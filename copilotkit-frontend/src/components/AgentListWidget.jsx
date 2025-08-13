// AgentListWidget.jsx
// Example CopilotKit dashboard widget using Apollo Client to fetch agents from GraphQL
import React from "react";
import { useQuery, gql } from "@apollo/client";

const AGENTS_QUERY = gql`
  query AvailableAgents {
    availableAgents {
      id
      name
      description
    }
  }
`;

export default function AgentListWidget() {
  const { loading, error, data } = useQuery(AGENTS_QUERY, {
    context: { uri: "/api/graphql" },
  });

  if (loading) return <div>Loading agents...</div>;
  if (error) return <div>Error loading agents: {error.message}</div>;

  return (
    <div>
      <h3>Available Agents</h3>
      <ul>
        {data.availableAgents.map(agent => (
          <li key={agent.id}>
            <strong>{agent.name}</strong>: {agent.description}
          </li>
        ))}
      </ul>
    </div>
  );
}
