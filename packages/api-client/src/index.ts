import type { GatewayResponse } from "@foxbrain/types";

/** Gateway-only browser client. It deliberately contains no database configuration. */
export function gatewayUrl(path: string, baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "") {
  if (!baseUrl) throw new Error("NEXT_PUBLIC_API_BASE_URL must be configured");
  return new URL(path, baseUrl).toString();
}

export async function gatewayFetch(path: string, init?: RequestInit) {
  return fetch(gatewayUrl(path), { ...init, headers: { Accept: "application/json", ...init?.headers } });
}

export async function gatewayJson<T>(path: string, init?: RequestInit): Promise<GatewayResponse<T>> {
  const response = await gatewayFetch(path, init);
  if (!response.ok) throw new Error(`Gateway request failed: ${response.status}`);
  return response.json() as Promise<GatewayResponse<T>>;
}
