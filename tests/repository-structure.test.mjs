import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";
const required = ["apps/gateway-web", "apps/ai-web", "apps/huyan-web", "packages/foxbrain-ui", "packages/api-client", "packages/types"];
test("frontend foundation packages exist", () => required.forEach(path => assert.ok(existsSync(path), path)));
test("frontend integration is gateway-only", () => { for (const app of ["ai-web", "huyan-web"]) { const source = readFileSync(`apps/${app}/app/page.tsx`, "utf8"); assert.match(source, /gatewayFetch/); assert.doesNotMatch(source, /postgres|redis|mongodb|DATABASE_URL/i); } });
test("design system provides all Outdoor Life OS card contracts", () => { const cards = readFileSync("packages/foxbrain-ui/src/index.tsx", "utf8"); for (const field of ["title", "summary", "evidence", "confidence", "action", "source", "timestamp", "version", "agent", "status", "tasks", "insights", "problem", "analysis", "options", "recommendation", "metric", "value", "trend"]) assert.match(cards, new RegExp(`\\b${field}\\b`)); });
test("portal defines RBAC protected Universe destinations", () => { const portal = readFileSync("apps/gateway-web/app/page.tsx", "utf8"); for (const value of ["Outdoor LIFE", "FoxBrain", "Huyan Intelligence", "Control", "employee", "ceo", "admin", "huyan.vafox.com", "ai.vafox.com", "control.vafox.com"]) assert.match(portal, new RegExp(value.replaceAll(".", "\\."))); assert.match(portal, /portal\.roles\.includes\(role\)/); });
test("API client requires a configured Gateway URL", () => { const client = readFileSync("packages/api-client/src/index.ts", "utf8"); assert.match(client, /NEXT_PUBLIC_API_BASE_URL/); assert.match(client, /gatewayFetch/); assert.match(client, /gatewayJson/); });

test("Huyan IA V1.1 keeps the confirmed navigation and production CEO API", () => {
  const source = readFileSync("apps/huyan-web/app/page.tsx", "utf8");
  const labels = ["CEO Today", "经营分析", "商品分析", "库存分析", "客户分析", "组织分析", "供应链分析", "AI顾问"];
  let previous = -1;
  for (const label of labels) {
    const current = source.indexOf(`"${label}"`);
    assert.ok(current > previous, `${label} must appear in the confirmed navigation order`);
    previous = current;
  }
  for (const section of ["AI 经营摘要", "六个核心经营指标", "五店经营状态", "风险预警", "TOP 品牌", "客户机会 TOP5"])
    assert.match(source, new RegExp(section));
  assert.match(source, /gatewayFetch\("\/api\/ceo\/today"\)/);
  assert.doesNotMatch(source, /mock(Data)?|fixture|faker/i);
});

test("Huyan V1.3 stabilization keeps the contract and exposes trustworthy empty and provenance states", () => {
  const source = readFileSync("apps/huyan-web/app/page.tsx", "utf8");
  for (const label of ["数据来源", "更新时间", "数据鲜度", "今日暂无品牌销售排行", "品牌排行暂不可用"])
    assert.match(source, new RegExp(label));
  assert.match(source, /gatewayFetch\("\/api\/ceo\/today"\)/);
  assert.doesNotMatch(source, /gatewayFetch\("\/api\/ceo\/overview"\)/);
  assert.doesNotMatch(source, /className="brand-mark"/);
});
