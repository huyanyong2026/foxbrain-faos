import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";
const required = ["apps/gateway-web", "apps/ai-web", "apps/huyan-web", "apps/control-web", "services/identity", "services/runtime", "services/knowledge", "services/product-intelligence", "services/customer-brain", "services/retail-brain", "services/core-data", "packages/ui", "packages/api-client", "packages/types", "infrastructure/docker", "infrastructure/nginx", "infrastructure/kubernetes", "infrastructure/monitoring", "docs/architecture", "docs/api", "docs/deployment", "docs/governance"];
test("architecture freeze directories exist", () => required.forEach(path => assert.ok(existsSync(path), path)));
test("frontend configuration uses the API Gateway", () => { for (const app of ["ai-web", "huyan-web"]) { const source = readFileSync(`apps/${app}/app/page.tsx`, "utf8"); assert.match(source, /gatewayFetch/); assert.doesNotMatch(source, /postgres|redis|mongodb|DATABASE_URL/i); } });
test("gitignore protects secrets and local dependencies", () => { const ignored = readFileSync(".gitignore", "utf8"); for (const value of [".env", "node_modules/", "venv/", "*credential*"]) assert.match(ignored, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))); });
