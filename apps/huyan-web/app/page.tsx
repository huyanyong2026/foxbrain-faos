"use client";
import { useEffect, useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";
import { DecisionCard, InsightCard } from "@foxbrain/ui";
export default function HuyanPage() { const [status, setStatus] = useState("正在加载只读经营摘要…"); useEffect(() => { gatewayFetch("/api/ceo/dashboard").then(response => setStatus(response.ok ? "经营摘要已更新；所有建议需人工确认。" : "暂时无法加载经营摘要。")); }, []); return <main><p className="eyebrow">FOX BRAIN / HUYAN</p><h1>虎眼 CEO AI Cockpit</h1><p className="lead">经营数据仅通过 API Gateway 读取；不含任何数据库直连能力。</p><p>{status}</p><div className="grid"><InsightCard title="销售摘要"><p>读取 Core Read Only API 摘要。</p></InsightCard><InsightCard title="库存提醒"><p>关注门店尺码结构与可售状态。</p></InsightCard><InsightCard title="AI 建议"><p>先复核重点客户需求，再安排员工跟进。</p></InsightCard><DecisionCard title="决策关口"><p>董事会、价格与库存决策均保留人工审批。</p></DecisionCard></div></main>; }
