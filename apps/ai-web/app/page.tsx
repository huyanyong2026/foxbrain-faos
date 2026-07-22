"use client";
import { useState } from "react";

type CardProps = { title: string; children: React.ReactNode };
export function AICard({ title, children }: CardProps) { return <section><h2>{title}</h2>{children}</section>; }
export const ProductCard = ({ product }: { product: string }) => <AICard title="Product Card"><strong>{product}</strong><p>产品建议仅供人工核实与使用。</p></AICard>;
export const CustomerCard = ({ customer }: { customer: string }) => <AICard title="Customer Card"><strong>{customer}</strong><p>仅向具备客户数据权限的员工展示。</p></AICard>;

export default function WorkspacePage() {
  const [query, setQuery] = useState("MONT适合什么客户？"); const [result, setResult] = useState("输入问题后获取只读建议。"); const [store, setStore] = useState("nanshan"); const [briefing, setBriefing] = useState("选择门店后获取店长今日重点。");
  async function ask() { const response = await fetch("/api/workspace/advice", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "product", query }) }); setResult(response.ok ? "已生成带 Citation 的产品建议；请人工核实价格、库存和尺码。" : "暂时无法获取建议。"); }
  async function loadBriefing() { const response = await fetch(`/api/store/dashboard?store=${store}`); setBriefing(response.ok ? "已加载销售摘要、商品机会、库存提醒与客户机会；请店长人工确认后安排任务。" : "暂时无法获取门店摘要或您没有该门店权限。"); }
  return <main><h1>VAFOX Employee AI Workspace</h1><p>查询 · 分析 · 建议（不执行销售、下单或数据修改）</p><AICard title="Store Manager Workspace"><label htmlFor="store">门店</label><select id="store" value={store} onChange={e => setStore(e.target.value)}><option value="nanshan">南山店</option><option value="hangyuan">航苑店</option><option value="zhenxing">振兴店</option></select><button onClick={loadBriefing}>今天重点是什么？</button><p>{briefing}</p><small>销售摘要 · 商品机会 · 库存提醒 · 客户机会 · AI建议</small></AICard><AICard title="Product Assistant"><input aria-label="AI 问题" value={query} onChange={e => setQuery(e.target.value)} /><button onClick={ask}>获取建议</button><p>{result}</p></AICard><ProductCard product="KAILAS MONT" /><CustomerCard customer="授权客户查询" /></main>;
}
