import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync("apps/huyan-web/app/page.tsx", "utf8");

test("CEO Today exposes the production AI daily report entry and API", () => {
  assert.match(page, /今日AI经营日报/);
  assert.match(page, /href="#daily-report"/);
  assert.match(page, /gatewayFetch\("\/api\/ceo\/daily-report\/latest"\)/);
});

test("daily report renders the governed four sections and unified contract", () => {
  for (const label of ["经营总结", "经营机会", "经营风险", "CEO行动建议", "结论", "依据", "建议", "数据来源", "更新时间", "可信度"])
    assert.match(page, new RegExp(label));
  assert.match(page, /report\.sections\[key\]/);
  assert.doesNotMatch(page, /mock(Data)?|fixture|faker/i);
});

test("daily report fails closed without substitute content", () => {
  assert.match(page, /日报暂不可用/);
  assert.match(page, /未取得可验证的已发布日报，不展示替代内容/);
  assert.match(page, /!\["published", "degraded"\]\.includes\(payload\.status\)/);
});
