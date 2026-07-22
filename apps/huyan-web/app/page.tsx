"use client";
import { useEffect, useState } from "react";
export function InsightCard({ title, items }: { title: string; items: string[] }) { return <section><h2>{title}</h2><ul>{items.map(item => <li key={item}>{item}</li>)}</ul></section>; }
export default function HuyanPage() { const [status, setStatus] = useState("正在加载只读经营摘要…"); useEffect(() => { fetch("/api/ceo/dashboard").then(response => setStatus(response.ok ? "经营摘要已更新；所有建议需人工确认。" : "暂时无法加载经营摘要。")); }, []); return <main><h1>Huyan CEO AI Cockpit</h1><p>{status}</p><InsightCard title="销售摘要" items={["读取 Core Read Only API 摘要"]} /><InsightCard title="库存提醒" items={["关注门店尺码结构与可售状态"]} /><InsightCard title="AI 建议" items={["先复核重点客户需求，再安排员工跟进"]} /></main>; }
