export type DeploymentEnvironment = "development" | "test" | "production";
export type GatewayResponse<T> = { data: T; requestId?: string };

export type Evidence = { source: string; timestamp: string; version: string; confidence: string };
export type AgentStatus = "active" | "watching" | "blocked";
export type RbacRole = "ceo" | "employee" | "admin";
export type WorkspaceDestination = "outdoor" | "ai" | "huyan" | "control";
