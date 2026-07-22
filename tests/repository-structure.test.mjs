import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";
const required = ["apps/gateway-web", "apps/ai-web", "apps/huyan-web", "packages/foxbrain-ui", "packages/api-client", "packages/types"];
test("frontend foundation packages exist", () => required.forEach(path => assert.ok(existsSync(path), path)));
test("frontend integration is gateway-only", () => { for (const app of ["ai-web", "huyan-web"]) { const source = readFileSync(`apps/${app}/app/page.tsx`, "utf8"); assert.match(source, /gatewayFetch/); assert.doesNotMatch(source, /postgres|redis|mongodb|DATABASE_URL/i); } });
test("design system provides all Outdoor Life OS card contracts", () => { const cards = readFileSync("packages/foxbrain-ui/src/index.tsx", "utf8"); for (const field of ["title", "summary", "evidence", "confidence", "action", "source", "timestamp", "version", "agent", "status", "tasks", "insights", "problem", "analysis", "options", "recommendation", "metric", "value", "trend"]) assert.match(cards, new RegExp(`\\b${field}\\b`)); });
test("portal defines RBAC protected Universe destinations", () => { const portal = readFileSync("apps/gateway-web/app/page.tsx", "utf8"); for (const value of ["Outdoor LIFE", "FoxBrain", "Huyan Intelligence", "Control", "employee", "ceo", "admin", "huyan.vafox.com", "ai.vafox.com", "control.vafox.com"]) assert.match(portal, new RegExp(value.replaceAll(".", "\\."))); assert.match(portal, /portal\.roles\.includes\(role\)/); });
test("API client requires a configured Gateway URL", () => { const client = readFileSync("packages/api-client/src/index.ts", "utf8"); assert.match(client, /NEXT_PUBLIC_API_BASE_URL/); assert.match(client, /gatewayFetch/); assert.match(client, /gatewayJson/); });
