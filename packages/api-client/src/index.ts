/** Gateway-only browser client. It deliberately contains no database configuration. */
export function gatewayUrl(path: string, baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "") {
  if (!baseUrl) throw new Error("NEXT_PUBLIC_API_BASE_URL must be configured");
  return new URL(path, baseUrl).toString();
}
export async function gatewayFetch(path: string, init?: RequestInit) { return fetch(gatewayUrl(path), init); }
