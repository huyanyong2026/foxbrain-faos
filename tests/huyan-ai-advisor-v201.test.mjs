import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync("apps/huyan-web/app/page.tsx", "utf8");
const gateway = readFileSync("services/gateway/app.py", "utf8");

test("Huyan V2.0.1 advisor provides the fixed answer contract and unavailable state", () => {
  for (const label of ["结论", "依据", "建议", "数据来源", "更新时间", "可信度", "AI服务暂不可用"])
    assert.match(page, new RegExp(label));
  assert.match(page, /gatewayFetch\("\/api\/ceo\/ai-advisor"/);
  assert.match(page, /常用经营问题/);
});

test("advisor requests all six governed contexts without accepting browser permission fields", () => {
  for (const domain of ["sales", "product", "inventory", "customer", "employee", "supply_chain"])
    assert.match(gateway, new RegExp(`"${domain}"`));
  assert.match(gateway, /VAFOX_CEO/);
  assert.match(gateway, /ALL_DATA/);
  assert.match(gateway, /advisor_request\.get\("question"/);
  assert.doesNotMatch(page, /permission_scope|is_ceo_identity/);
});
