import type { Evidence, AgentStatus } from "@foxbrain/types";

type CardProps = { children: React.ReactNode; className?: string; label: string; title: string };
function Card({ children, className = "", label, title }: CardProps) {
  return <article className={`fox-card ${className}`}><p className="card-label">{label}</p><h2>{title}</h2>{children}</article>;
}
export type AICardProps = { title: string; summary: string; evidence: string; confidence: string; action: string };
export function AICard({ title, summary, evidence, confidence, action }: AICardProps) {
  return <Card label="AI 建议" title={title} className="ai-card"><p>{summary}</p><p className="card-action">{action}</p><footer><span>{evidence}</span><b>{confidence}</b></footer></Card>;
}
export function EvidenceCard({ source, timestamp, version, confidence }: Evidence) {
  return <Card label="已验证证据" title={source}><dl><div><dt>采集时间</dt><dd>{timestamp}</dd></div><div><dt>数据版本</dt><dd>{version}</dd></div><div><dt>可信度</dt><dd>{confidence}</dd></div></dl></Card>;
}
export type AgentCardProps = { agent: string; status: AgentStatus; tasks: string; insights: string };
export function AgentCard({ agent, status, tasks, insights }: AgentCardProps) {
  return <Card label={`智能模块 · ${status === "active" ? "运行中" : "关注中"}`} title={agent}><dl><div><dt>任务</dt><dd>{tasks}</dd></div><div><dt>洞察</dt><dd>{insights}</dd></div></dl></Card>;
}
export type DecisionCardProps = { problem: string; analysis: string; options: string; recommendation: string };
export function DecisionCard({ problem, analysis, options, recommendation }: DecisionCardProps) {
  return <Card label="待确认决策" title={problem}><dl><div><dt>分析</dt><dd>{analysis}</dd></div><div><dt>选项</dt><dd>{options}</dd></div></dl><p className="card-action">{recommendation}</p></Card>;
}
export type DataCardProps = { metric: string; value: string; trend: string; source: string };
export function DataCard({ metric, value, trend, source }: DataCardProps) {
  return <Card label="核心数据" title={metric} className="data-card"><strong className="metric-value">{value}</strong><p className="trend">{trend}</p><footer><span>{source}</span></footer></Card>;
}
