import type { ReactNode } from "react";

export type BrainCardProps = { title: string; eyebrow?: string; children: ReactNode };
export function BrainCard({ title, eyebrow, children }: BrainCardProps) {
  return <section className="brain-card">{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2><div>{children}</div></section>;
}
export const AICard = BrainCard;
export function ProductCard({ product, children }: { product: string; children?: ReactNode }) { return <BrainCard eyebrow="PRODUCT" title={product}>{children ?? <p>通过 Gateway 获取商品洞察。</p>}</BrainCard>; }
export function CustomerCard({ customer, children }: { customer: string; children?: ReactNode }) { return <BrainCard eyebrow="CUSTOMER" title={customer}>{children ?? <p>仅展示当前授权范围内的客户信息。</p>}</BrainCard>; }
export function InsightCard({ title, children }: BrainCardProps) { return <BrainCard eyebrow="INSIGHT" title={title}>{children}</BrainCard>; }
export function DecisionCard({ title, children }: BrainCardProps) { return <BrainCard eyebrow="DECISION" title={title}>{children}</BrainCard>; }
