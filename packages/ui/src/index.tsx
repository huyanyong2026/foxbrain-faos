import type { ReactNode } from "react";

type CardFrameProps = { eyebrow: string; title: string; children: ReactNode; className?: string };

export function BrainCard({ eyebrow, title, children, className = "" }: CardFrameProps) {
  return <article className={`brain-card ${className}`}><p className="eyebrow">{eyebrow}</p><h2>{title}</h2>{children}</article>;
}

export type AICardProps = { question: string; analysis: string; recommendation: string; citation: string; confidence: string };
export function AICard({ question, analysis, recommendation, citation, confidence }: AICardProps) {
  return <BrainCard eyebrow="AI ANALYSIS" title={question} className="ai-card"><p className="card-copy">{analysis}</p><p className="recommendation">{recommendation}</p><footer><span>{citation}</span><strong>{confidence}</strong></footer></BrainCard>;
}

export type ProductCardProps = { product: string; brand: string; scenario: string; recommendation: string };
export function ProductCard({ product, brand, scenario, recommendation }: ProductCardProps) {
  return <BrainCard eyebrow={brand} title={product}><dl><div><dt>适用场景</dt><dd>{scenario}</dd></div><div><dt>推荐动作</dt><dd>{recommendation}</dd></div></dl></BrainCard>;
}

export type CustomerCardProps = { customer: string; profile: string; equipment: string; opportunity: string };
export function CustomerCard({ customer, profile, equipment, opportunity }: CustomerCardProps) {
  return <BrainCard eyebrow="CUSTOMER OPPORTUNITY" title={customer}><dl><div><dt>客户画像</dt><dd>{profile}</dd></div><div><dt>现有装备</dt><dd>{equipment}</dd></div><div><dt>机会</dt><dd>{opportunity}</dd></div></dl></BrainCard>;
}

export type InsightCardProps = { metric: string; risk: string; opportunity: string; source: string };
export function InsightCard({ metric, risk, opportunity, source }: InsightCardProps) {
  return <BrainCard eyebrow="BUSINESS SIGNAL" title={metric}><dl><div><dt>风险</dt><dd>{risk}</dd></div><div><dt>机会</dt><dd>{opportunity}</dd></div></dl><footer><span>{source}</span></footer></BrainCard>;
}

export type DecisionCardProps = { problem: string; options: string; impact: string; approval: string };
export function DecisionCard({ problem, options, impact, approval }: DecisionCardProps) {
  return <BrainCard eyebrow="DECISION REQUIRED" title={problem}><dl><div><dt>可选方案</dt><dd>{options}</dd></div><div><dt>影响</dt><dd>{impact}</dd></div></dl><p className="approval">{approval}</p></BrainCard>;
}
