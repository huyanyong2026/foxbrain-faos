"use client";

import { useEffect, useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";

type Risk = { type: string; title: string; severity: string; message: string };
type IntelligenceItem = { conclusion?: string; evidence?: string[]; recommendation?: string[] };
type SalesChange = { dimension: "store" | "brand" | "category" | "customer"; name: string; change?: number | string; reasons: string[]; evidence?: string[] };
type CapitalRisk = { risk: string; reason: string; recommendation: string; severity?: string };
type BrandScore = { brand_name: string; sales_contribution?: number | string; trend?: number | string; inventory_health?: number | string; customer_recognition?: number | string; overall_score?: number | string };
type CustomerAction = { customer_name?: string; customer_segment?: string; action: string; reason: string; priority?: string };
type Dashboard = {
  ai_summary: string;
  ai_evidence?: string[];
  sales: number;
  orders: number;
  inventory_amount?: number;
  operating_stores: { store_code: string; store_name: string; status: string }[];
  top_brands: { brand_name: string; sales: number; trend?: number | string }[];
  risks: Risk[];
  effective_skus: number;
  customer_opportunities: { title: string; reason: string; opportunity_type?: string; recommended_action?: string }[];
  ai_recommendations: string[];
  data_source: string;
  updated_at: string;
  confidence: number | string;
  freshness_status?: string;
  today_intelligence?: IntelligenceItem;
  sales_change_analysis?: SalesChange[];
  inventory_capital_risks?: CapitalRisk[];
  brand_operating_scores?: BrandScore[];
  customer_actions?: CustomerAction[];
};

const navItems = [["CEO Today", "today"], ["经营分析", "operations"], ["商品分析", "products"], ["库存分析", "inventory"], ["客户分析", "customers"], ["组织分析", "organization"], ["供应链分析", "supply-chain"], ["AI顾问", "advisor"]] as const;
type SectionKey = typeof navItems[number][1];
const analysisModules: Record<Exclude<SectionKey, "today" | "advisor">, { eyebrow: string; title: string; description: string; items: string[] }> = {
  operations: { eyebrow: "BUSINESS ANALYSIS", title: "经营分析", description: "从整体到店铺、员工、顾客与供应商，统一查看销售表现。", items: ["整体销售分析", "店铺销售分析", "员工销售分析", "顾客购买分析", "供应商销售分析"] },
  products: { eyebrow: "PRODUCT ANALYSIS", title: "商品分析", description: "围绕商品结构、销售贡献与补货决策展开分析。", items: ["品牌", "品类", "SKU", "采购建议"] },
  inventory: { eyebrow: "INVENTORY ANALYSIS", title: "库存分析", description: "识别库存资金占用、健康度与周转风险。", items: ["库存金额", "有效库存", "滞销", "缺货", "周转"] },
  customers: { eyebrow: "CUSTOMER ANALYSIS", title: "客户分析", description: "在授权范围内理解客户、分层客户并发现经营机会。", items: ["Customer360", "客户分层", "客户机会"] },
  organization: { eyebrow: "ORGANIZATION ANALYSIS", title: "组织分析", description: "从个人与团队两个层级观察组织经营贡献。", items: ["员工销售", "团队表现"] },
  "supply-chain": { eyebrow: "SUPPLY CHAIN", title: "供应链分析", description: "联动供应商、采购与库存，提升供应链协同效率。", items: ["供应商", "采购", "库存协同"] },
};
const activeStores = ["zhenxing", "nanshan", "hangyuan", "jinsha", "online"];
const riskTypes = [["库存风险", "inventory"], ["销售异常", "sales"], ["客户风险", "customer"], ["供应链风险", "supply"], ["数据异常", "data"]];
const unavailable = "数据暂不可用。";
const money = (value: number) => new Intl.NumberFormat("zh-CN", { style: "currency", currency: "CNY", maximumFractionDigits: 0 }).format(value);
const statusLabel = (status: string) => status === "ACTIVE" ? "正常营业" : status;
const riskMatches = (risk: Risk, key: string) => risk.type.toLowerCase().includes(key);
const trendLabel = (trend?: number | string) => trend === undefined ? unavailable : typeof trend === "number" ? `${trend >= 0 ? "+" : ""}${trend}%` : trend;
const dimensionLabels = { store: "门店", brand: "品牌", category: "品类", customer: "客户" };
const scoreLabel = (value?: number | string) => value === undefined ? unavailable : typeof value === "number" ? `${value.toFixed(0)} / 100` : value;

export default function HuyanPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [status, setStatus] = useState("正在同步经营数据");
  const [failed, setFailed] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionKey>("today");

  useEffect(() => {
    gatewayFetch("/api/ceo/today")
      .then(async (response) => {
        if (!response.ok) throw new Error(String(response.status));
        const report = await response.json() as Dashboard;
        if (
          ![report.sales, report.orders, report.effective_skus].every(Number.isFinite)
          || !report.data_source
          || !report.updated_at
          || !Array.isArray(report.operating_stores)
          || !Array.isArray(report.top_brands)
          || !Array.isArray(report.risks)
          || !Array.isArray(report.customer_opportunities)
          || !Array.isArray(report.ai_recommendations)
        ) throw new Error("invalid_ceo_api_payload");
        setData(report);
        setStatus("数据已更新");
      })
      .catch(() => { setFailed(true); setStatus(unavailable); });
  }, []);

  useEffect(() => {
    const syncSection = () => {
      const section = window.location.hash.slice(1) as SectionKey;
      if (navItems.some(([, key]) => key === section)) setActiveSection(section);
    };
    syncSection();
    window.addEventListener("hashchange", syncSection);
    return () => window.removeEventListener("hashchange", syncSection);
  }, []);

  const metrics = [
    { label: "销售额", value: failed ? unavailable : data ? money(data.sales) : "—", note: "五店今日合计", tone: "primary" },
    { label: "订单数", value: failed ? unavailable : data?.orders ?? "—", suffix: data ? " 单" : "", note: "今日有效订单" },
    { label: "客单价", value: failed ? unavailable : data && data.orders > 0 ? money(data.sales / data.orders) : "—", note: "销售额 / 订单数" },
    { label: "库存金额", value: failed ? unavailable : data?.inventory_amount === undefined ? unavailable : money(data.inventory_amount), note: "仅展示 API 返回值" },
    { label: "有效 SKU", value: failed ? unavailable : data?.effective_skus ?? "—", suffix: data ? " 个" : "", note: "当前有效商品" },
    { label: "客户机会", value: failed ? unavailable : data?.customer_opportunities.length ?? "—", suffix: data ? " 条" : "", note: "已授权机会", tone: data?.customer_opportunities.length ? "warning" : "status" },
  ];

  const sectionMeta = activeSection !== "today" && activeSection !== "advisor" ? analysisModules[activeSection] : null;
  const todayIntelligence = data?.today_intelligence;
  const conclusion = todayIntelligence?.conclusion ?? data?.ai_summary;
  const evidence = todayIntelligence?.evidence ?? data?.ai_evidence;
  const recommendations = todayIntelligence?.recommendation ?? data?.ai_recommendations;

  return <div className="portal-shell">
    <aside className="sidebar">
      <div className="brand-lockup"><span className="brand-mark">V</span><strong>VAFOX</strong></div>
      <div className="portal-name"><span>HUYAN</span><b>CEO Portal</b></div>
      <nav aria-label="CEO Portal 主导航">{navItems.map(([label, anchor], index) => <a className={activeSection === anchor ? "is-active" : ""} href={`#${anchor}`} key={anchor} aria-current={activeSection === anchor ? "page" : undefined}><i>{String(index + 1).padStart(2, "0")}</i><span>{label}</span></a>)}</nav>
      <div className="sidebar-foot"><span>管理层专用</span><small>只读 · 安全数据链</small></div>
    </aside>
    <main className="app-shell">
    <header className="topbar">
      <div className="mobile-brand"><span className="brand-mark">V</span><strong>VAFOX CEO Portal</strong></div>
      <div className="current-location"><span>CEO PORTAL</span><strong>{navItems.find(([, key]) => key === activeSection)?.[0]}</strong></div>
      <div className="header-meta"><span className={`data-state ${data ? "is-live" : ""}`}><i />{status}</span><span className="access-badge">管理层专用</span><span className="avatar">CEO</span></div>
    </header>
    {activeSection === "today" && <>
    <section className="welcome" id="today" aria-labelledby="page-title">
      <div><p className="eyebrow">CEO TODAY</p><h1 id="page-title">今日经营全景</h1><p>聚焦关键结果、经营风险与下一步动作。</p></div>
      <div className="scope"><span>经营范围</span><strong>振兴 · 南山 · 航苑 · 金沙 · 网店</strong><small>只读 · API 实时数据</small></div>
    </section>

    <section className="ai-summary executive-summary" id="advisor" aria-labelledby="ai-title">
      <div className="panel-kicker"><span className="ai-icon">AI</span><div><p id="ai-title">AI 经营摘要</p><small>AI 不覆盖事实数据，仅提供辅助判断</small></div><span className="confidence-chip">可信状态 · {failed ? unavailable : data?.confidence ?? "—"}</span></div>
      <div className="summary-columns">
        <div><span>结论</span><blockquote>{failed ? unavailable : conclusion ?? "正在读取经营摘要…"}</blockquote></div>
        <div><span>依据</span>{failed || (data && !evidence?.length) ? <p>{unavailable}</p> : evidence?.length ? <ul>{evidence.map((item) => <li key={item}>{item}</li>)}</ul> : <p>正在读取数据依据…</p>}</div>
        <div><span>建议</span>{failed || (data && !recommendations?.length) ? <p>{unavailable}</p> : <ol>{recommendations?.slice(0, 3).map((item) => <li key={item}>{item}</li>)}</ol>}</div>
      </div>
      <footer><span><b>数据来源</b>{failed ? unavailable : data?.data_source ?? "—"}</span><span><b>更新时间</b>{failed ? unavailable : data?.updated_at ?? "—"}</span><span><b>数据鲜度</b>{failed ? unavailable : data?.freshness_status ?? "—"}</span></footer>
    </section>

    <section className="metrics-grid" id="operations" aria-label="六个核心经营指标">{metrics.map((metric) => <article className={`metric-card ${metric.tone ?? ""}`} key={metric.label}><div className="metric-head"><span>{metric.label}</span><i>↗</i></div><strong>{metric.value}<small>{metric.suffix}</small></strong><p>{metric.note}</p></article>)}</section>

    <section className="section-block" id="organization">
      <div className="section-title"><div><p className="eyebrow">STORE STATUS</p><h2>五店经营状态</h2></div><span className="quiet-badge">仅当前经营主体</span></div>
      <div className="store-grid">{failed ? <p className="empty-state">{unavailable}</p> : data ? activeStores.map((storeCode) => {
        const store = data.operating_stores.find((item) => item.store_code === storeCode);
        return <article className={!store ? "is-unavailable" : ""} key={storeCode}><span className="store-icon">店</span><div><strong>{store?.store_name ?? unavailable}</strong><small>{store ? <><i />{statusLabel(store.status)}</> : unavailable}</small></div></article>;
      }) : <p className="empty-state">正在读取门店状态…</p>}</div>
    </section>

    <section className="section-block risk-panel" id="inventory">
      <div className="section-title compact"><div><p className="eyebrow">RISK ALERT</p><h2>风险预警</h2></div><span className={`risk-count ${failed ? "is-unavailable" : ""}`}>{failed ? "—" : data?.risks.length ?? "—"}</span></div>
      <div className="risk-categories">{riskTypes.map(([label, key]) => <div key={key}><span>{label}</span><strong>{failed ? unavailable : data ? data.risks.filter((risk) => riskMatches(risk, key)).length : "—"}</strong></div>)}</div>
      <div className="risk-list">{failed ? <p className="empty-state">{unavailable}</p> : data?.risks.slice(0, 5).map((risk) => <div className="risk-item" key={`${risk.type}-${risk.title}`}><span>!</span><div><strong>{risk.title}</strong><p>{risk.message}</p></div><small>{risk.severity}</small></div>) ?? <p className="empty-state">正在读取风险数据…</p>}{data && data.risks.length === 0 && <p className="empty-state">当前没有需要处理的风险。</p>}</div>
    </section>

    <section className="bottom-grid">
      <article className="table-panel" id="products"><div className="section-title compact"><div><p className="eyebrow">BRAND SALES</p><h2>TOP 品牌</h2></div><span className="period">今日</span></div><div className="brand-head"><span>品牌名称</span><span>销售额</span><span>趋势</span></div><div className="brand-list">{failed ? <p className="empty-state">{unavailable}</p> : data?.top_brands.length ? data.top_brands.slice(0, 5).map((brand, index) => <div className="brand-row" key={brand.brand_name}><b>{String(index + 1).padStart(2, "0")}</b><strong>{brand.brand_name}</strong><span>{money(brand.sales)}</span><em>{trendLabel(brand.trend)}</em></div>) : <p className="empty-state">{data ? unavailable : "正在读取品牌销售…"}</p>}</div></article>
      <article className="table-panel" id="customers"><div className="section-title compact"><div><p className="eyebrow">CUSTOMER OPPORTUNITY</p><h2>客户机会 TOP5</h2></div><span className="customer-only">仅授权客户</span></div><div className="opportunity-list">{data?.customer_opportunities.slice(0, 5).map((item, index) => <div className="opportunity-row" key={`${item.title}-${index}`}><b>{index + 1}</b><div><strong>{item.title}</strong><small>{item.opportunity_type ?? unavailable}</small><p>{item.reason}</p></div><span>{item.recommended_action ?? unavailable}</span></div>) ?? <p className="empty-state">{failed ? unavailable : "正在读取客户机会…"}</p>}{data && data.customer_opportunities.length === 0 && <p className="empty-state">当前暂无已授权客户机会。</p>}</div></article>
    </section>

    </>}

    {sectionMeta && <section className="analysis-page" id={activeSection} aria-labelledby="analysis-title">
      <div className="analysis-hero"><p className="eyebrow">{sectionMeta.eyebrow}</p><h1 id="analysis-title">{sectionMeta.title}</h1><p>{sectionMeta.description}</p></div>
      <div className="analysis-grid">{sectionMeta.items.map((item, index) => <article key={item}><span>{String(index + 1).padStart(2, "0")}</span><div><h2>{item}</h2><p>沿用现有权限与 CEO API 数据口径</p></div><b aria-hidden="true">→</b></article>)}</div>
      {activeSection === "operations" && <div className="intelligence-panel"><div className="section-title compact"><div><p className="eyebrow">CHANGE DRIVER</p><h2>销售变化原因分析</h2></div></div><div className="intelligence-list">{data?.sales_change_analysis?.length ? data.sales_change_analysis.map((item) => <article key={`${item.dimension}-${item.name}`}><div className="intel-heading"><span>{dimensionLabels[item.dimension]}</span><strong>{item.name}</strong><em>{trendLabel(item.change)}</em></div><div className="intel-detail"><b>原因</b><p>{item.reasons.join("；")}</p><b>依据</b><p>{item.evidence?.join("；") || unavailable}</p></div></article>) : <p className="empty-state">{failed ? unavailable : data ? "Core API 暂未返回销售变化原因分析。" : "正在读取销售变化分析…"}</p>}</div></div>}
      {activeSection === "inventory" && <div className="intelligence-panel"><div className="section-title compact"><div><p className="eyebrow">CAPITAL RISK</p><h2>库存资金风险分析</h2></div></div><div className="three-part-list">{data?.inventory_capital_risks?.length ? data.inventory_capital_risks.map((item) => <article key={item.risk}><span>{item.severity ?? "风险"}</span><div><b>风险</b><p>{item.risk}</p></div><div><b>原因</b><p>{item.reason}</p></div><div><b>建议</b><p>{item.recommendation}</p></div></article>) : <p className="empty-state">{failed ? unavailable : data ? "Core API 暂未返回库存资金风险分析。" : "正在读取库存资金风险…"}</p>}</div></div>}
      {activeSection === "products" && <div className="intelligence-panel"><div className="section-title compact"><div><p className="eyebrow">BRAND SCORECARD</p><h2>品牌经营评分</h2></div></div><div className="score-table"><div className="score-head"><span>品牌</span><span>销售贡献</span><span>趋势</span><span>库存健康</span><span>客户认可</span><span>综合评分</span></div>{data?.brand_operating_scores?.length ? data.brand_operating_scores.map((item) => <div className="score-row" key={item.brand_name}><strong>{item.brand_name}</strong><span>{scoreLabel(item.sales_contribution)}</span><span>{trendLabel(item.trend)}</span><span>{scoreLabel(item.inventory_health)}</span><span>{scoreLabel(item.customer_recognition)}</span><b>{scoreLabel(item.overall_score)}</b></div>) : <p className="empty-state">{failed ? unavailable : data ? "Core API 暂未返回品牌经营评分。" : "正在读取品牌评分…"}</p>}</div></div>}
      {activeSection === "customers" && <div className="intelligence-panel"><div className="section-title compact"><div><p className="eyebrow">CUSTOMER360 ACTION</p><h2>客户行动建议</h2></div><span className="customer-only">基于 Customer360 · 仅授权客户</span></div><div className="customer-actions">{data?.customer_actions?.length ? data.customer_actions.map((item, index) => <article key={`${item.customer_name}-${index}`}><span>{item.priority ?? String(index + 1).padStart(2, "0")}</span><div><strong>{item.customer_name ?? item.customer_segment ?? "授权客户"}</strong><small>{item.customer_segment}</small><p>{item.reason}</p></div><b>{item.action}</b></article>) : <p className="empty-state">{failed ? unavailable : data ? "Core API 暂未返回 Customer360 行动建议。" : "正在读取客户行动建议…"}</p>}</div></div>}
      <div className="architecture-note"><span>数据连接保持不变</span><p>SAP B1 · Data Core · CEO API · Auth · AI Runtime</p></div>
    </section>}

    {activeSection === "advisor" && <section className="advisor-page" id="advisor" aria-labelledby="advisor-title">
      <div className="advisor-hero"><span className="ai-icon">AI</span><div><p className="eyebrow">CEO BUSINESS ADVISOR</p><h1 id="advisor-title">AI顾问</h1><p>CEO经营问答</p></div></div>
      <div className="advisor-card"><label htmlFor="ceo-question">向 AI 顾问提出经营问题</label><div><input id="ceo-question" placeholder="例如：今天最需要关注的经营风险是什么？" /><button type="button">开始分析</button></div><small>基于现有 AI Runtime 与授权经营数据提供辅助判断，不改变事实数据。</small></div>
      <div className="question-prompts"><span>常用问题</span>{["五店销售表现有什么异常？", "哪些库存风险需要优先处理？", "本周最值得跟进的客户机会是什么？"].map((question) => <button type="button" key={question}>{question}<b>→</b></button>)}</div>
      <div className="advisor-answer"><div><span>结论</span><p>{failed ? unavailable : conclusion ?? "请提出经营问题。"}</p></div><div><span>依据</span><p>{failed ? unavailable : evidence?.join("；") || unavailable}</p></div><div><span>建议</span><p>{failed ? unavailable : recommendations?.join("；") || unavailable}</p></div><footer><span><b>数据来源</b>{failed ? unavailable : data?.data_source ?? "—"}</span><span><b>更新时间</b>{failed ? unavailable : data?.updated_at ?? "—"}</span></footer></div>
    </section>}
    <footer className="page-footer"><span>VAFOX CEO Portal · huyan.vafox.com</span><span>董事、CEO 与授权管理层专用 · 页面只读</span></footer>
    </main>
  </div>;
}
