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

type TraceablePayload = { data_source?: string; updated_at?: string; freshness_status?: string; data_status?: string };
type SalesRecord = { store_code?: string; store_name?: string; sales?: number; sales_amount?: number; orders?: number; order_count?: number; average_order_value?: number; trend?: number | string; status?: string };
type SalesPayload = TraceablePayload & SalesRecord & { summary?: SalesRecord; stores?: SalesRecord[]; trend_series?: { label?: string; date?: string; value?: number }[]; ai_advice?: IntelligenceItem };
type MemberRecord = { member_id?: string; employee_id?: string; name?: string; display_name?: string; store_name?: string; sales?: number; sales_amount?: number; orders?: number; order_count?: number; trend?: number | string };
type MembersPayload = TraceablePayload & { members?: MemberRecord[]; summary?: { coverage_rate?: number; pending_rows?: number } };
type CustomerPayload = TraceablePayload & { customers?: { customer_id: string; customer_name?: string; consumption_amount?: number; purchase_count?: number; value_segment?: string; opportunity?: string }[] };
type SupplierPayload = TraceablePayload & { domain?: "supply_chain"; suppliers?: { supplier_id?: string; supplier_code?: string; supplier_name?: string; name?: string; purchase_amount?: number; purchase_count?: number; delivery_status?: string }[] };
type LoadState<T> = { phase: "loading" | "ready" | "empty" | "forbidden" | "error"; data?: T };

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
const provenanceValue = (value?: string) => value?.trim() || "等待 CEO API 返回";
const pending = "待补齐";
const stores = [{ code: "zhenxing", name: "振兴" }, { code: "nanshan", name: "南山" }, { code: "hangyuan", name: "航苑" }, { code: "jinsha", name: "金沙" }, { code: "online", name: "网店" }] as const;
const numeric = (value: unknown): value is number => typeof value === "number" && Number.isFinite(value);
const saleValue = (record?: SalesRecord) => numeric(record?.sales_amount) ? record.sales_amount : numeric(record?.sales) ? record.sales : undefined;
const orderValue = (record?: SalesRecord) => numeric(record?.order_count) ? record.order_count : numeric(record?.orders) ? record.orders : undefined;
const averageValue = (record?: SalesRecord) => {
  if (numeric(record?.average_order_value)) return record.average_order_value;
  const sales = saleValue(record); const orders = orderValue(record);
  return numeric(sales) && numeric(orders) && orders > 0 ? sales / orders : undefined;
};
const metric = (value: number | undefined, kind: "money" | "count" = "count") => numeric(value) ? (kind === "money" ? money(value) : value.toLocaleString("zh-CN")) : pending;

function Provenance({ payload, state }: { payload?: TraceablePayload; state: LoadState<unknown>["phase"] }) {
  const stateText = state === "loading" ? "正在读取" : state === "forbidden" ? "无权查看该经营范围" : state === "error" ? "数据暂不可用" : state === "empty" ? "当前范围暂无数据" : payload?.data_status || payload?.freshness_status || "数据状态待补齐";
  return <div className="analysis-provenance"><span><b>数据来源</b>{payload?.data_source || "数据溯源待补齐"}</span><span><b>更新时间</b>{payload?.updated_at || pending}</span><span><b>数据状态</b>{stateText}</span></div>;
}

function BusinessAnalysis() {
  const [sales, setSales] = useState<LoadState<SalesPayload>>({ phase: "loading" });
  const [members, setMembers] = useState<LoadState<MembersPayload>>({ phase: "loading" });
  const [customers, setCustomers] = useState<LoadState<CustomerPayload>>({ phase: "loading" });
  const [suppliers, setSuppliers] = useState<LoadState<SupplierPayload>>({ phase: "loading" });
  const load = async <T,>(path: string, update: (state: LoadState<T>) => void) => {
    update({ phase: "loading" });
    try {
      const response = await gatewayFetch(path);
      if (response.status === 401 || response.status === 403) return update({ phase: "forbidden" });
      if (!response.ok) return update({ phase: "error" });
      const payload = await response.json() as T;
      const candidate = payload as Record<string, unknown>;
      const empty = Array.isArray(candidate.data) && candidate.data.length === 0;
      update({ phase: empty ? "empty" : "ready", data: payload });
    } catch { update({ phase: "error" }); }
  };
  useEffect(() => { void load("/api/business/sales-analysis", setSales); void load("/api/business/member-analysis", setMembers); void load("/api/business/customer-analysis", setCustomers); void load("/api/business/supplier-analysis", setSuppliers); }, []);
  const summary = sales.data?.summary || sales.data;
  const memberRows = members.data?.members || [];
  const stateMessage = (state: LoadState<unknown>) => state.phase === "loading" ? "正在读取…" : state.phase === "forbidden" ? "无权查看该经营范围" : state.phase === "error" ? "数据暂不可用，请稍后重试" : state.phase === "empty" ? "当前范围暂无数据" : "";
  const retry = () => { void load("/api/business/sales-analysis", setSales); void load("/api/business/member-analysis", setMembers); void load("/api/business/customer-analysis", setCustomers); void load("/api/business/supplier-analysis", setSuppliers); };
  const advice = sales.data?.ai_advice;
  return <section className="business-analysis" id="operations" aria-labelledby="business-title">
    <div className="analysis-hero business-hero"><div><p className="eyebrow">BUSINESS ANALYSIS · V1.4</p><h1 id="business-title">经营分析</h1><p>基于授权经营范围，查看整体、门店、员工、顾客与供应商表现。</p></div><button type="button" onClick={retry}>刷新数据</button></div>

    <article className="business-module"><div className="module-title"><span>01</span><div><h2>整体销售分析</h2><p>销售额、订单数、客单价与销售趋势</p></div></div><Provenance payload={sales.data} state={sales.phase} />
      {sales.phase === "ready" ? <><div className="business-metrics"><div><span>销售额</span><strong>{metric(saleValue(summary), "money")}</strong></div><div><span>订单数</span><strong>{metric(orderValue(summary))}</strong></div><div><span>客单价</span><strong>{metric(averageValue(summary), "money")}</strong><small>{!numeric(summary?.average_order_value) && numeric(averageValue(summary)) ? "销售额 / 订单数" : "API 返回值"}</small></div><div><span>趋势</span><strong>{trendLabel(summary?.trend).replace(unavailable, pending)}</strong></div></div><div className="trend-strip" aria-label="销售趋势">{sales.data?.trend_series?.length ? sales.data.trend_series.map((point, index) => <div key={`${point.date || point.label}-${index}`}><span>{point.label || point.date || pending}</span><strong>{numeric(point.value) ? money(point.value) : pending}</strong></div>) : <p>{pending}</p>}</div></> : <p className="module-state">{stateMessage(sales)}</p>}
    </article>

    <article className="business-module"><div className="module-title"><span>02</span><div><h2>店铺销售分析</h2><p>固定经营主体 · 按稳定门店编码匹配</p></div></div><Provenance payload={sales.data} state={sales.phase} /><div className="store-analysis-grid">{stores.map((store) => { const row = sales.data?.stores?.find((item) => item.store_code === store.code); return <section key={store.code} className={!row ? "is-pending" : ""}><header><h3>{store.name}</h3><b>{row?.status || pending}</b></header><dl><div><dt>销售</dt><dd>{metric(saleValue(row), "money")}</dd></div><div><dt>订单</dt><dd>{metric(orderValue(row))}</dd></div><div><dt>趋势</dt><dd>{trendLabel(row?.trend).replace(unavailable, pending)}</dd></div></dl></section>; })}</div></article>

    <article className="business-module"><div className="module-title"><span>03</span><div><h2>员工销售分析</h2><p>仅展示成员 API 返回的授权销售字段</p></div></div><Provenance payload={members.data} state={members.phase} />{members.phase === "ready" && memberRows.length ? <div className="member-table"><div className="member-table-head"><span>员工</span><span>门店</span><span>销售</span><span>订单</span><span>趋势</span></div>{memberRows.map((row, index) => <div key={row.member_id || row.employee_id || index}><strong>{row.display_name || row.name || pending}</strong><span>{row.store_name || pending}</span><span>{metric(saleValue(row), "money")}</span><span>{metric(orderValue(row))}</span><span>{trendLabel(row.trend).replace(unavailable, pending)}</span></div>)}</div> : <p className="module-state">{members.phase === "ready" ? "销售数据待补齐" : stateMessage(members)}</p>}</article>

    <div className="domain-grid"><article className="business-module"><div className="module-title"><span>04</span><div><h2>顾客购买分析</h2><p>Customer360 独立客户事实域</p></div></div><Provenance payload={customers.data} state={customers.phase} />{customers.phase === "ready" && customers.data?.customers?.length ? <div className="member-table">{customers.data.customers.map((row) => <div key={row.customer_id}><strong>{row.customer_name || "授权客户"}</strong><span>{metric(row.consumption_amount, "money")}</span><span>{metric(row.purchase_count)}</span><span>{row.value_segment || pending}</span><span>{row.opportunity || pending}</span></div>)}</div> : <p className="module-state">{stateMessage(customers) || "客户数据待补齐"}</p>}</article><article className="business-module supplier-domain"><div className="module-title"><span>05</span><div><h2>供应商销售分析</h2><p>独立供应链数据域 · 不混入客户数据</p></div></div><Provenance payload={suppliers.data} state={suppliers.phase} />{suppliers.phase === "ready" && suppliers.data?.suppliers?.length ? <div className="member-table">{suppliers.data.suppliers.map((row, index) => <div key={row.supplier_id || row.supplier_code || index}><strong>{row.supplier_name || row.name || pending}</strong><span>{metric(row.purchase_amount, "money")}</span><span>{metric(row.purchase_count)}</span><span>{row.delivery_status || pending}</span></div>)}</div> : <p className="module-state">{stateMessage(suppliers) || "供应链数据待补齐"}</p>}</article></div>

    <article className="business-module ai-advice"><div className="module-title"><span>AI</span><div><h2>经营建议</h2><p>AI 不覆盖事实，仅展示接口返回的辅助判断</p></div></div><div className="advice-grid"><div><span>结论</span><p>{advice?.conclusion || pending}</p></div><div><span>依据</span><p>{advice?.evidence?.join("；") || pending}</p></div><div><span>建议</span><p>{advice?.recommendation?.join("；") || pending}</p></div></div></article>
  </section>;
}

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

  const sectionMeta = activeSection !== "today" && activeSection !== "advisor" && activeSection !== "operations" ? analysisModules[activeSection] : null;
  const todayIntelligence = data?.today_intelligence;
  const conclusion = todayIntelligence?.conclusion ?? data?.ai_summary;
  const evidence = todayIntelligence?.evidence ?? data?.ai_evidence;
  const recommendations = todayIntelligence?.recommendation ?? data?.ai_recommendations;

  return <div className="portal-shell">
    <aside className="sidebar">
      <div className="brand-lockup" aria-label="VAFOX"><strong>VAFOX</strong><span>®</span></div>
      <div className="portal-name"><span>HUYAN</span><b>CEO Portal</b></div>
      <nav aria-label="CEO Portal 主导航">{navItems.map(([label, anchor], index) => <a className={activeSection === anchor ? "is-active" : ""} href={`#${anchor}`} key={anchor} aria-current={activeSection === anchor ? "page" : undefined}><i>{String(index + 1).padStart(2, "0")}</i><span>{label}</span></a>)}</nav>
      <div className="sidebar-foot"><span>管理层专用</span><small>只读 · 安全数据链</small></div>
    </aside>
    <main className="app-shell">
    <header className="topbar">
      <div className="mobile-brand" aria-label="VAFOX CEO Portal"><strong>VAFOX</strong><span>CEO Portal</span></div>
      <div className="current-location"><span>CEO PORTAL</span><strong>{navItems.find(([, key]) => key === activeSection)?.[0]}</strong></div>
      <div className="header-meta"><span className={`data-state ${data ? "is-live" : ""}`}><i />{status}</span><span className="access-badge">管理层专用</span><span className="avatar">CEO</span></div>
    </header>
    {activeSection === "today" && <>
    <section className="welcome" id="today" aria-labelledby="page-title">
      <div><p className="eyebrow">CEO TODAY</p><h1 id="page-title">今日经营全景</h1><p>聚焦关键结果、经营风险与下一步动作。</p></div>
      <div className="scope"><span>经营范围</span><strong>振兴 · 南山 · 航苑 · 金沙 · 网店</strong><small>只读 · API 实时数据</small></div>
    </section>

    <section className="data-provenance" aria-label="数据来源与更新时间" aria-live="polite">
      <span><b>数据来源</b><strong>{failed ? unavailable : provenanceValue(data?.data_source)}</strong></span>
      <span><b>更新时间</b><strong>{failed ? unavailable : provenanceValue(data?.updated_at)}</strong></span>
      <span><b>数据鲜度</b><strong>{failed ? unavailable : provenanceValue(data?.freshness_status)}</strong></span>
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
      <article className="table-panel" id="products"><div className="section-title compact"><div><p className="eyebrow">BRAND SALES</p><h2>TOP 品牌</h2></div><span className="period">今日</span></div><div className="brand-head"><span>品牌名称</span><span>销售额</span><span>趋势</span></div><div className="brand-list">{failed ? <div className="brand-empty is-error"><span aria-hidden="true">!</span><div><strong>品牌排行暂不可用</strong><p>经营数据读取失败，请稍后刷新页面。</p></div></div> : data?.top_brands.length ? data.top_brands.slice(0, 5).map((brand, index) => <div className="brand-row" key={brand.brand_name}><b>{String(index + 1).padStart(2, "0")}</b><strong>{brand.brand_name}</strong><span>{money(brand.sales)}</span><em>{trendLabel(brand.trend)}</em></div>) : data ? <div className="brand-empty"><span aria-hidden="true">—</span><div><strong>今日暂无品牌销售排行</strong><p>当前筛选范围内没有品牌销售记录，数据口径保持不变。</p></div></div> : <div className="brand-empty is-loading"><span aria-hidden="true">•••</span><div><strong>正在读取品牌销售</strong><p>排行将在 CEO API 返回后自动显示。</p></div></div>}</div></article>
      <article className="table-panel" id="customers"><div className="section-title compact"><div><p className="eyebrow">CUSTOMER OPPORTUNITY</p><h2>客户机会 TOP5</h2></div><span className="customer-only">仅授权客户</span></div><div className="opportunity-list">{data?.customer_opportunities.slice(0, 5).map((item, index) => <div className="opportunity-row" key={`${item.title}-${index}`}><b>{index + 1}</b><div><strong>{item.title}</strong><small>{item.opportunity_type ?? unavailable}</small><p>{item.reason}</p></div><span>{item.recommended_action ?? unavailable}</span></div>) ?? <p className="empty-state">{failed ? unavailable : "正在读取客户机会…"}</p>}{data && data.customer_opportunities.length === 0 && <p className="empty-state">当前暂无已授权客户机会。</p>}</div></article>
    </section>

    </>}

    {activeSection === "operations" && <BusinessAnalysis />}
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
