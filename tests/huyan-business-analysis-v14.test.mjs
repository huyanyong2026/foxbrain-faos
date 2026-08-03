import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../apps/huyan-web/app/page.tsx", import.meta.url), "utf8");

test("business analysis uses only its declared Core API contracts", () => {
  assert.match(page, /load\("\/api\/core\/sales"/);
  assert.match(page, /load\("\/api\/core\/members"/);
  assert.equal((page.match(/gatewayFetch\("\/api\/ceo\/today"\)/g) || []).length, 1);
});

test("the five stores are fixed and missing facts remain pending", () => {
  for (const name of ["振兴", "南山", "航苑", "金沙", "网店"]) assert.match(page, new RegExp(`name: "${name}"`));
  assert.match(page, /const pending = "待补齐"/);
  assert.match(page, /供应链数据待补齐/);
});

test("customer and supplier domains have separate render containers", () => {
  assert.match(page, /Customer360 独立客户事实域/);
  assert.match(page, /className="business-module domain-pending supplier-domain"/);
  assert.match(page, /独立供应链数据域 · 不混入客户数据/);
});
