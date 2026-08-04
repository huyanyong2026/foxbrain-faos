import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync("apps/huyan-web/app/page.tsx", "utf8");

test("CEO Today exposes the real AI daily report API entry", () => {
  assert.match(page, /今日AI经营日报/);
  assert.match(page, /gatewayFetch\("\/api\/ceo\/daily-report\/latest"\)/);
  assert.doesNotMatch(page, /mock|fixture|faker/i);
});

test("daily report renders four sections with the unified evidence format", () => {
  for (const label of ["经营总结", "经营机会", "经营风险", "CEO行动建议", "结论", "依据", "建议", "数据来源", "更新时间", "可信度", "日报暂不可用"])
    assert.match(page, new RegExp(label));
  for (const key of ["business_summary", "business_opportunities", "business_risks", "ceo_actions"])
    assert.match(page, new RegExp(key));
});
