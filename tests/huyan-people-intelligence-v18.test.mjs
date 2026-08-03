import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync("apps/huyan-web/app/page.tsx", "utf8");
test("organization page uses its real API and includes all five modules", () => {
  assert.match(page, /gatewayFetch\("\/api\/business\/organization-analysis"\)/);
  for (const label of ["员工总览", "员工销售分析", "员工能力分析", "团队分析", "成长建议"]) assert.match(page, new RegExp(label));
  for (const label of ["振兴", "南山", "航苑", "金沙", "网店"]) assert.match(page, new RegExp(label));
  assert.match(page, /销售归属待补齐/); assert.match(page, /不平均分配、不推测贡献/);
});
