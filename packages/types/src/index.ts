export type DeploymentEnvironment = "development" | "test" | "production";
export type GatewayResponse<T> = { data: T; requestId?: string };
