import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync("apps/huyan-web/app/page.tsx", "utf8");

test("Huyan Supply Chain V1.9 uses the real governed endpoint", () => {
  assert.match(page, /gatewayFetch\(`\/api\/business\/supply-chain-intelligence\?\$\{query\}`\)/);
  assert.match(page, /date_from/);
  assert.match(page, /date_to/);
  assert.doesNotMatch(page, /mock|fixture|faker/i);
});

test("Huyan Supply Chain V1.9 exposes every required decision section and syncing state", () => {
  for (const label of ["供应链总览", "供应商表现", "品牌供应关系", "采购协同", "供应链风险", "AI建议", "供应链数据同步中。"]) {
    assert.match(page, new RegExp(label));
  }
  assert.match(page, /activeSection === "supply-chain" && <SupplyChainIntelligence/);
});
