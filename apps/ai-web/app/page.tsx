"use client";
import { useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";
import { AICard, CustomerCard, DecisionCard, ProductCard } from "@foxbrain/ui";

const modules = ["Sales AI", "Store AI", "Product AI", "Learning AI"];
export default function WorkspacePage() {
  const [query, setQuery] = useState("哪位客户最适合本周的轻量徒步装备？");
  const [answer, setAnswer] = useState("准备好基于授权范围生成建议。");
  const [loading, setLoading] = useState(false);
  async function ask() {
    setLoading(true);
    try { const response = await gatewayFetch("/api/workspace/advice", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "sales", query }) }); setAnswer(response.ok ? "建议已生成，并等待员工确认下一步动作。" : "暂时无法获取建议，请稍后再试。"); }
    catch { setAnswer("无法连接 API Gateway，请检查网络或权限。"); }
    finally { setLoading(false); }
  }
  return <main className="app-shell"><header className="topbar"><a className="brand" href="#top">VAFOX <span>FOX BRAIN</span></a><nav aria-label="工作台模块">{modules.map((item, index) => <a className={index === 0 ? "active" : ""} href={`#${item}`} key={item}>{item}</a>)}</nav><button className="avatar" aria-label="打开个人菜单">LX</button></header><section id="top" className="hero"><p className="eyebrow">DIGITAL EMPLOYEE / 07.22</p><div><h1>让今天的每一次服务<br />都更接近成交。</h1><p className="lead">早上好，林晓。FoxBrain 已为你梳理今日最值得行动的客户、商品与门店信号。</p></div><aside className="today"><span>今日任务</span><strong>06</strong><p>3 项客户跟进 · 2 项库存处理 · 1 项学习任务</p></aside></section><section className="section-heading"><div><p className="eyebrow">PRIORITY QUEUE</p><h2>从一个高价值机会开始</h2></div><button className="text-button">查看全部任务 →</button></section><section className="workspace-grid"><CustomerCard customer="陈奕 · 南山店" profile="周末轻徒步爱好者，近 30 天到店 2 次" equipment="MONT 25L 背包、徒步鞋" opportunity="推荐新到防水外壳；预计机会 ¥1,680" /><ProductCard product="MONT 轻量防水外壳" brand="KAILAS" scenario="周末轻徒步 / 15–22°C 阵雨" recommendation="优先向陈奕等 12 位相似客户展示" /><AICard question="今天先联系谁？" analysis="陈奕的兴趣与库存可售尺码高度匹配，且最近浏览过同系列装备。" recommendation="在午间发送一次个性化搭配建议。" citation="Customer Brain · Retail Brain" confidence="置信度 89%" /></section><section className="assistant"><div><p className="eyebrow">ASK FOXBRAIN</p><h2>你的 AI 助手</h2><p>所有业务数据均通过 API Gateway 在当前授权范围内读取。</p></div><div className="ask-box"><label htmlFor="question">问一个与工作相关的问题</label><div><input id="question" value={query} onChange={(event) => setQuery(event.target.value)} /><button onClick={ask} disabled={loading}>{loading ? "分析中…" : "发送"}</button></div><p aria-live="polite">{answer}</p></div></section><section className="workspace-grid"><DecisionCard problem="南山店 M 尺码库存偏低" options="调拨 8 件 / 建立预售名单" impact="避免本周末潜在流失，预计保护 ¥6,400 销售机会" approval="需要店长确认后执行" /></section></main>;
}
