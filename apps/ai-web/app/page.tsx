"use client";
import { useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";
import { AICard, CustomerCard, DecisionCard, ProductCard } from "@foxbrain/ui";

export default function WorkspacePage() {
  const [query, setQuery] = useState("MONT适合什么客户？");
  const [result, setResult] = useState("输入问题后获取只读建议。");
  const [store, setStore] = useState("nanshan");
  const [briefing, setBriefing] = useState("选择门店后获取店长今日重点。");
  async function ask() { const response = await gatewayFetch("/api/workspace/advice", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "product", query }) }); setResult(response.ok ? "已生成带 Citation 的产品建议；请人工核实价格、库存和尺码。" : "暂时无法获取建议。"); }
  async function loadBriefing() { const response = await gatewayFetch(`/api/store/dashboard?store=${store}`); setBriefing(response.ok ? "已加载销售摘要、商品机会、库存提醒与客户机会；请店长人工确认后安排任务。" : "暂时无法获取门店摘要或您没有该门店权限。"); }
  return <main><p className="eyebrow">FOX BRAIN / EMPLOYEE WORKSPACE</p><h1>员工 AI 工作台</h1><p className="lead">所有读取请求经由 API Gateway；工作台不直接访问数据库，也不执行业务写入。</p><div className="grid"><AICard title="Store Manager Workspace"><label htmlFor="store">门店</label><select id="store" value={store} onChange={e => setStore(e.target.value)}><option value="nanshan">南山店</option><option value="hangyuan">航苑店</option><option value="zhenxing">振兴店</option></select><button onClick={loadBriefing}>今天重点是什么？</button><p>{briefing}</p></AICard><AICard title="Product Assistant"><input aria-label="AI 问题" value={query} onChange={e => setQuery(e.target.value)} /><button onClick={ask}>获取建议</button><p>{result}</p></AICard><ProductCard product="KAILAS MONT" /><CustomerCard customer="授权客户查询" /><DecisionCard title="人工决策关口"><p>AI 输出是建议，价格、库存和客户动作须由授权员工确认。</p></DecisionCard></div></main>;
}
