import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const page = readFileSync(new URL("../apps/huyan-web/app/page.tsx", import.meta.url), "utf8");

test("customer page uses the real Customer360 aggregation endpoint and four modules", () => {
  assert.match(page, /gatewayFetch\("\/api\/business\/customer-intelligence"\)/);
  for (const title of ["客户总览", "客户价值分层", "购买行为分析", "客户机会池"]) assert.match(page, new RegExp(title));
  for (const label of ["客户数量", "活跃客户", "消费金额", "订单数量", "平均消费", "VIP数量"]) assert.match(page, new RegExp(label));
});

test("opportunity and WeCom contracts remain factual and read-only", () => {
  for (const label of ["复购", "升级", "召回", "交叉销售", "原因", "依据", "建议动作", "负责人"]) assert.match(page, new RegExp(label));
  assert.match(page, /接口已预留 · 未启用推送 · 不自动执行/);
  assert.doesNotMatch(page, /mock|fixture|faker/i);
});
