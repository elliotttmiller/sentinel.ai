// CopilotKit runtime client configuration for correct endpoint separation
import { CopilotRuntimeClientGQL } from "@copilotkit/runtime-client-gql";

export const runtimeClient = new CopilotRuntimeClientGQL({
  endpoint: "/api/graphql", // GraphQL queries/mutations
  // Add other config as needed
});
