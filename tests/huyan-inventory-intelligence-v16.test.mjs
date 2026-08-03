import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../apps/huyan-web/app/page.tsx", import.meta.url), "utf8");

test("inventory page uses one real aggregation API and all four modules", () => {
  assert.match(page, /gatewayFetch\("\/api\/business\/inventory-analysis"\)/);
  for (const title of ["库存总览", "库存健康分析", "滞销库存分析", "补货建议"]) assert.match(page, new RegExp(title));
  for (const status of ["正常库存", "高库存", "滞销库存", "缺货风险"]) assert.match(page, new RegExp(status));
});

test("inventory scope and governed cost state are explicit", () => {
  assert.match(page, /effective_skus/);
  assert.match(page, /成本数据治理中/);
  assert.doesNotMatch(page, /mock|fixture|faker/i);
});
