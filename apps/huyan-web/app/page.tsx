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
type ProductPayload = TraceablePayload & { cost_status?: string; cost_message?: string; brands?: { brand_name: string; sales_amount: number; sales_share: number; sku_count: number; inventory_amount: number; movement_status: string }[]; categories?: { category_name: string; sales_amount: number; sales_share: number; trend?: number; inventory_quantity: number }[]; skus?: { hot: ProductSku[]; risk: ProductSku[]; items: ProductSku[] }; procurement_recommendations?: { conclusion: string; evidence: string; recommendation: string }[] };
type ProductSku = { sku: string; product_name: string; sales_amount: number; inventory_quantity: number; movement_status: string; risk_status: string; trend?: number };
type InventoryItem = { sku: string; product_name: string; brand_name: string; inventory_amount: number; inventory_quantity: number; last_sale_date?: string; inventory_age_days?: number; health_status: "正常库存" | "高库存" | "滞销库存" | "缺货风险"; risk_level: string; recommendation: string; sales_velocity: number; trend?: number };
type InventoryPayload = TraceablePayload & { cost_status: string; cost_message?: string; scope: { dataset: "effective_skus"; excluded: string[] }; overview: { inventory_amount: number; effective_skus: number; inventory_quantity: number; brand_structure: { name: string; quantity: number; share: number }[]; store_structure: { name: string; quantity: number; share: number }[] }; health: Record<InventoryItem["health_status"], InventoryItem[]>; items: InventoryItem[]; slow_moving: InventoryItem[]; replenishment_recommendations: { conclusion: string; evidence: string; recommendation: string }[] };
type CustomerOpportunity = { customer_id: string; customer: string; opportunity_type: "复购" | "升级" | "召回" | "交叉销售"; reason?: string; evidence?: string; recommended_action?: string; owner?: string };
type CustomerIntelligencePayload = TraceablePayload & { overview: { customer_count: number; active_customers: number; consumption_amount: number; order_count: number; average_consumption: number; vip_count: number }; value_segments: { name: "VIP" | "高价值" | "成长" | "正常" | "流失风险"; count: number }[]; purchase_behavior: { brand_preferences: { customer_id: string; customer_name: string; preference: string }[]; category_preferences: { customer_id: string; customer_name: string; preference: string }[]; purchase_cycles: { customer_id: string; customer_name: string; purchase_cycle: string | number }[]; purchase_trends: { customer_id: string; customer_name: string; purchase_trend: string | number }[] }; customer_opportunities: CustomerOpportunity[]; wecom: { interface_reserved: true; delivery_enabled: false } };
type PeopleEmployee = { employee_id: string; employee: string; store_name: string; attribution_status: string; sales_amount: number; order_count: number; average_order_value: number; trend_series: { date: string; value: number }[]; capability: { sales: { sales_amount: number; order_count: number }; product: { distinct_products: number }; customer: { distinct_customers: number } } };
type PeoplePayload = TraceablePayload & { overview: { employee_count: number; selling_employee_count: number; sales_coverage_rate: number; order_count: number; attributed_sales: number; pending_order_count: number; pending_sales: number }; employees: PeopleEmployee[]; teams: { store_code: string; team: string; employee_count: number; team_sales: number; sales_per_employee?: number; trend_series: { date: string; value: number }[] }[]; growth_advice: { conclusion: string; evidence: string[]; recommendation: string[] } };
type SupplyChainPayload = {
  version: string; read_only: boolean; domain: "supply_chain";
  data_status: { status: string; message?: string | null; sources: { name: string; status: string; updated_at?: string | null }[]; limitations: string[] };
  overview: { supplier_count: number; purchase_order_count: number; purchase_quantity: number; purchase_amount: number | null; received_quantity: number | null; receipt_rate: number | null; on_time_rate: number | null; open_quantity: number | null; brand_count: number } | null;
  supplier_performance: { supplier_id: string; supplier_name: string; supplier_status: string; purchase_order_count: number; purchase_amount: number | null; receipt_rate: number | null; on_time_rate: number | null; open_quantity: number | null; brand_count: number; last_purchase_date: string }[];
  brand_supply_relationships: { brand_id: string; brand_name?: string | null; supplier_count: number; suppliers: { supplier_id: string; supplier_name: string }[]; purchase_quantity: number; purchase_amount: number | null; inventory_quantity: number; last_purchase_date: string }[];
  procurement_collaboration: { purchase_document_ref: string; supplier_name: string; brand_name?: string | null; sku_id: string; order_date: string; expected_delivery_date?: string | null; received_date?: string | null; ordered_quantity: number; received_quantity: number | null; open_quantity: number | null; document_status: string; inventory_quantity?: number | null }[];
  risks: { risk_id: string; risk_type: string; supplier_id: string; brand_id?: string | null; sku_id: string; purchase_document_ref: string; conclusion: string; evidence: Record<string, unknown>[] }[];
  ai_advice: { status: string; items: { conclusion?: string; evidence?: string[]; recommendation?: string[] }[] };
  trace?: { request_id?: string; generated_at?: string; source_names?: string[] };
};
type PeopleSort = "employee" | "store_name" | "sales_amount" | "order_count" | "average_order_value";
type LoadState<T> = { phase: "loading" | "ready" | "empty" | "forbidden" | "error"; data?: T };
type AdvisorResponse = { content?: string; source?: string; confidence?: number | string; generated_at?: string; citations?: { source?: string; statement?: string }[] };

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

const advisorPrompts = ["五店销售表现有什么异常？", "哪些库存风险需要优先处理？", "本周最值得跟进的客户机会是什么？", "哪些商品需要调整经营策略？", "员工与供应链有哪些协同风险？"];
const advisorSection = (content: string, labels: string[]) => {
  const line = content.split("\n").find((item) => labels.some((label) => item.startsWith(`${label}：`)));
  return line?.slice(line.indexOf("：") + 1).trim() || "—";
};

function AIAdvisor() {
  const [question, setQuestion] = useState("");
  const [phase, setPhase] = useState<"idle" | "loading" | "ready" | "forbidden" | "error">("idle");
  const [answer, setAnswer] = useState<AdvisorResponse>();
  const ask = async (selected = question) => {
    const value = selected.trim();
    if (!value || phase === "loading") return;
    setQuestion(value); setPhase("loading"); setAnswer(undefined);
    try {
      const response = await gatewayFetch("/api/ceo/ai-advisor", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: value }) });
      if (response.status === 401 || response.status === 403) return setPhase("forbidden");
      if (!response.ok) return setPhase("error");
      setAnswer(await response.json() as AdvisorResponse); setPhase("ready");
    } catch { setPhase("error"); }
  };
  const content = answer?.content || "";
  const conclusion = advisorSection(content, ["结论", "经营摘要"]);
  const evidence = answer?.citations?.map((item) => item.statement || item.source).filter(Boolean).join("；") || advisorSection(content, ["依据", "数据依据"]);
  const recommendation = advisorSection(content, ["建议", "AI建议", "建议行动"]);
  return <section className="advisor-page" id="advisor" aria-labelledby="advisor-title">
    <div className="advisor-hero"><span className="ai-icon">AI</span><div><p className="eyebrow">CEO BUSINESS ADVISOR · V2.0.1</p><h1 id="advisor-title">AI顾问</h1><p>连接销售、商品、库存、客户、员工与供应链经营上下文</p></div></div>
    <form className="advisor-card" onSubmit={(event) => { event.preventDefault(); void ask(); }}><label htmlFor="ceo-question">向 AI 顾问提出经营问题</label><div><input id="ceo-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="例如：今天最需要关注的经营风险是什么？" aria-describedby="advisor-scope" /><button type="submit" disabled={!question.trim() || phase === "loading"}>{phase === "loading" ? "分析中…" : "开始分析"}</button></div><small id="advisor-scope">仅基于 VAFOX_CEO · ALL_DATA 授权范围进行只读分析；问题文本不能扩大数据权限。</small></form>
    <div className="question-prompts"><span>常用经营问题</span>{advisorPrompts.map((prompt) => <button type="button" key={prompt} onClick={() => void ask(prompt)}>{prompt}<b>→</b></button>)}</div>
    {phase === "forbidden" && <div className="advisor-status" role="alert">无权使用 AI 顾问，仅 VAFOX_CEO · ALL_DATA 可访问。</div>}
    {phase === "error" && <div className="advisor-status is-error" role="alert">AI服务暂不可用</div>}
    {(phase === "idle" || phase === "loading") && <div className="advisor-status" aria-live="polite">{phase === "loading" ? "正在分析授权经营数据…" : "请选择常用问题或输入经营问题。"}</div>}
    {phase === "ready" && <div className="advisor-answer" aria-live="polite"><div><span>结论</span><p>{conclusion}</p></div><div><span>依据</span><p>{evidence}</p></div><div><span>建议</span><p>{recommendation}</p></div><footer><span><b>数据来源</b>{answer?.source || answer?.citations?.map((item) => item.source).filter(Boolean).join("、") || "—"}</span><span><b>更新时间</b>{answer?.generated_at ? new Date(answer.generated_at).toLocaleString("zh-CN") : "—"}</span><span><b>可信度</b>{answer?.confidence ?? "—"}</span></footer></div>}
  </section>;
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

function PeopleIntelligence() {
  const [state, setState] = useState<LoadState<PeoplePayload>>({ phase: "loading" });
  const [sort, setSort] = useState<PeopleSort>("sales_amount"); const [ascending, setAscending] = useState(false);
  const load = async () => { setState({ phase: "loading" }); try { const response = await gatewayFetch("/api/business/organization-analysis"); if (response.status === 401 || response.status === 403) return setState({ phase: "forbidden" }); if (!response.ok) return setState({ phase: "error" }); setState({ phase: "ready", data: await response.json() as PeoplePayload }); } catch { setState({ phase: "error" }); } };
  useEffect(() => { void load(); }, []); const data = state.data; const overview = data?.overview;
  const rows = [...(data?.employees || [])].sort((a, b) => { const av = a[sort]; const bv = b[sort]; const result = typeof av === "number" && typeof bv === "number" ? av - bv : String(av).localeCompare(String(bv), "zh-CN"); return ascending ? result : -result; });
  const changeSort = (key: PeopleSort) => { if (sort === key) setAscending(!ascending); else { setSort(key); setAscending(key === "employee" || key === "store_name"); } };
  const stateText = state.phase === "loading" ? "正在读取组织数据…" : state.phase === "forbidden" ? "无权查看该经营范围" : "组织数据暂不可用，请稍后重试";
  return <section className="business-analysis people-intelligence" id="organization" aria-labelledby="people-title"><div className="analysis-hero business-hero"><div><p className="eyebrow">PEOPLE INTELLIGENCE · V1.8</p><h1 id="people-title">组织分析</h1><p>只展示真实员工归属与销售事实，不平均分配、不推测贡献。</p></div><button type="button" onClick={() => void load()}>刷新数据</button></div><Provenance payload={data} state={state.phase} />
  {state.phase !== "ready" ? <p className="module-state">{stateText}</p> : <><article className="business-module"><div className="module-title"><span>01</span><div><h2>员工总览</h2><p>销售贡献仅统计已明确归属记录</p></div></div><div className="people-overview business-metrics"><div><span>员工数量</span><strong>{metric(overview?.employee_count)}</strong></div><div><span>有销售员工数量</span><strong>{metric(overview?.selling_employee_count)}</strong></div><div><span>销售覆盖率</span><strong>{numeric(overview?.sales_coverage_rate) ? `${(overview.sales_coverage_rate * 100).toFixed(1)}%` : pending}</strong></div><div><span>订单数量</span><strong>{metric(overview?.order_count)}</strong></div><div><span>销售贡献</span><strong>{metric(overview?.attributed_sales, "money")}</strong></div></div>{overview && overview.pending_order_count > 0 && <p className="attribution-warning">销售归属待补齐。待归属订单 {overview.pending_order_count} 笔，金额 {money(overview.pending_sales)}；未计入任何员工或团队。</p>}</article>
  <article className="business-module"><div className="module-title"><span>02</span><div><h2>员工销售分析</h2><p>点击表头排序</p></div></div><div className="people-table"><div className="people-head">{([["员工","employee"],["门店","store_name"],["销售额","sales_amount"],["订单","order_count"],["客单价","average_order_value"]] as [string,PeopleSort][]).map(([label,key]) => <button key={key} onClick={() => changeSort(key)}>{label}{sort === key ? (ascending ? " ↑" : " ↓") : ""}</button>)}<span>趋势</span></div>{rows.map(row => <div key={row.employee_id}><strong>{row.employee}</strong><span className={row.attribution_status === "pending" ? "pending-owner" : ""}>{row.store_name}</span><span>{money(row.sales_amount)}</span><span>{row.order_count}</span><span>{money(row.average_order_value)}</span><span>{row.trend_series.length ? row.trend_series.map(point => money(point.value)).join(" → ") : pending}</span></div>)}</div></article>
  <article className="business-module"><div className="module-title"><span>03</span><div><h2>员工能力分析</h2><p>销售、商品、客户能力均为可核验事实指标</p></div></div><div className="capability-grid">{rows.map(row => <section key={row.employee_id}><h3>{row.employee}</h3><div><span>销售能力</span><b>{money(row.capability.sales.sales_amount)} · {row.capability.sales.order_count} 单</b></div><div><span>商品能力</span><b>{row.capability.product.distinct_products} 个销售商品</b></div><div><span>客户能力</span><b>{row.capability.customer.distinct_customers} 位关联客户</b></div></section>)}</div></article>
  <article className="business-module"><div className="module-title"><span>04</span><div><h2>团队分析</h2><p>振兴 · 南山 · 航苑 · 金沙 · 网店</p></div></div><div className="team-grid">{data?.teams.map(team => <section key={team.store_code}><h3>{team.team}</h3><dl><div><dt>团队销售</dt><dd>{money(team.team_sales)}</dd></div><div><dt>人效</dt><dd>{numeric(team.sales_per_employee) ? money(team.sales_per_employee) : pending}</dd></div><div><dt>趋势</dt><dd>{team.trend_series.length ? team.trend_series.map(point => money(point.value)).join(" → ") : pending}</dd></div></dl></section>)}</div></article>
  <article className="business-module ai-advice"><div className="module-title"><span>05</span><div><h2>成长建议</h2><p>基于当前已归属事实</p></div></div><div className="advice-grid"><div><span>结论</span><p>{data?.growth_advice.conclusion}</p></div><div><span>依据</span><p>{data?.growth_advice.evidence.join("；")}</p></div><div><span>建议</span><p>{data?.growth_advice.recommendation.join("；")}</p></div></div></article></>}</section>;
}

function ProductIntelligence() {
  const [state, setState] = useState<LoadState<ProductPayload>>({ phase: "loading" });
  const load = async () => { setState({ phase: "loading" }); try { const response = await gatewayFetch("/api/business/product-analysis"); if (response.status === 401 || response.status === 403) return setState({ phase: "forbidden" }); if (!response.ok) return setState({ phase: "error" }); const payload = await response.json() as ProductPayload; setState({ phase: "ready", data: payload }); } catch { setState({ phase: "error" }); } };
  useEffect(() => { void load(); }, []);
  const data = state.data;
  const stateText = state.phase === "loading" ? "正在读取商品数据…" : state.phase === "forbidden" ? "无权查看该经营范围" : state.phase === "error" ? "商品数据暂不可用，请稍后重试" : "";
  return <section className="business-analysis product-intelligence" id="products" aria-labelledby="product-title">
    <div className="analysis-hero business-hero"><div><p className="eyebrow">PRODUCT INTELLIGENCE · V1.5</p><h1 id="product-title">商品分析</h1><p>基于真实销售、库存与趋势，识别商品结构和采购行动。</p></div><button type="button" onClick={() => void load()}>刷新数据</button></div>
    <Provenance payload={data} state={state.phase} />{state.phase !== "ready" && <p className="module-state">{stateText}</p>}
    {state.phase === "ready" && <>
      <article className="business-module"><div className="module-title"><span>01</span><div><h2>品牌分析</h2><p>品牌名称 · 销售额 · 销售占比 · SKU数量 · 库存金额 · 动销状态</p></div></div>{data?.cost_status !== "trusted" && <p className="cost-governance">{data?.cost_message || "成本数据治理中。"}</p>}<div className="product-table brand-analysis-table"><div><b>品牌名称</b><b>销售额</b><b>销售占比</b><b>SKU数量</b><b>库存金额</b><b>动销状态</b></div>{data?.brands?.map((row) => <div key={row.brand_name}><strong>{row.brand_name}</strong><span>{money(row.sales_amount)}</span><span>{(row.sales_share * 100).toFixed(1)}%</span><span>{row.sku_count}</span><span>{data.cost_status === "trusted" ? money(row.inventory_amount) : "成本数据治理中。"}</span><em>{row.movement_status}</em></div>)}</div></article>
      <article className="business-module"><div className="module-title"><span>02</span><div><h2>品类分析</h2><p>品类销售结构 · 趋势 · 库存结构</p></div></div><div className="category-cards">{data?.categories?.map((row) => <section key={row.category_name}><strong>{row.category_name}</strong><dl><div><dt>销售结构</dt><dd>{(row.sales_share * 100).toFixed(1)}%</dd></div><div><dt>趋势</dt><dd>{trendLabel(row.trend).replace(unavailable, pending)}</dd></div><div><dt>库存结构</dt><dd>{row.inventory_quantity.toLocaleString("zh-CN")}</dd></div></dl></section>)}</div></article>
      <article className="business-module"><div className="module-title"><span>03</span><div><h2>SKU分析</h2><p>热销SKU · 风险SKU · 库存 · 销售 · 动销</p></div></div><div className="product-table sku-analysis-table"><div><b>SKU / 商品</b><b>销售</b><b>库存</b><b>动销</b><b>风险</b></div>{data?.skus?.items.map((row) => <div key={row.sku}><strong>{row.product_name}<small>{row.sku}</small></strong><span>{money(row.sales_amount)}</span><span>{row.inventory_quantity}</span><em>{row.movement_status}</em><em>{row.risk_status}</em></div>)}</div></article>
      <article className="business-module"><div className="module-title"><span>04</span><div><h2>采购建议</h2><p>基于销售 · 库存 · 趋势</p></div></div><div className="advice-grid">{data?.procurement_recommendations?.length ? data.procurement_recommendations.map((row, index) => <div key={`${row.conclusion}-${index}`}><span>结论</span><p>{row.conclusion}</p><span>依据</span><p>{row.evidence}</p><span>建议</span><p>{row.recommendation}</p></div>) : <p className="module-state">当前没有采购风险建议</p>}</div></article>
    </>}
  </section>;
}


function InventoryIntelligence() {
  const [state, setState] = useState<LoadState<InventoryPayload>>({ phase: "loading" });
  const [healthFilter, setHealthFilter] = useState<InventoryItem["health_status"]>("正常库存");
  const load = async () => { setState({ phase: "loading" }); try { const response = await gatewayFetch("/api/business/inventory-analysis"); if (response.status === 401 || response.status === 403) return setState({ phase: "forbidden" }); if (!response.ok) return setState({ phase: "error" }); setState({ phase: "ready", data: await response.json() as InventoryPayload }); } catch { setState({ phase: "error" }); } };
  useEffect(() => { void load(); }, []);
  const data = state.data; const trusted = data?.cost_status === "trusted";
  const stateText = state.phase === "loading" ? "正在读取库存数据…" : state.phase === "forbidden" ? "无权查看该经营范围" : state.phase === "error" ? "库存数据暂不可用，请稍后重试" : "";
  const amount = (value: number) => trusted ? money(value) : "成本数据治理中";
  return <section className="business-analysis inventory-intelligence" id="inventory" aria-labelledby="inventory-title">
    <div className="analysis-hero business-hero"><div><p className="eyebrow">INVENTORY INTELLIGENCE · V1.6</p><h1 id="inventory-title">库存分析</h1><p>基于 effective_skus 识别库存结构、健康风险与补货行动。</p></div><button type="button" onClick={() => void load()}>刷新数据</button></div>
    <Provenance payload={data} state={state.phase} />{state.phase !== "ready" && <p className="module-state">{stateText}</p>}
    {data && <><div className="inventory-scope"><b>有效口径</b><span>{data.scope.dataset}</span><b>排除</b><span>{data.scope.excluded.join(" · ")}</span></div>
      {!trusted && <p className="cost-governance">{data.cost_message || "成本数据治理中"}</p>}
      <article className="business-module"><div className="module-title"><span>01</span><div><h2>库存总览</h2><p>库存金额 · 有效SKU数量 · 库存数量 · 品牌与门店库存结构</p></div></div><div className="business-metrics inventory-metrics"><div><span>库存金额</span><strong>{amount(data.overview.inventory_amount)}</strong></div><div><span>有效SKU数量</span><strong>{data.overview.effective_skus.toLocaleString("zh-CN")}</strong></div><div><span>库存数量</span><strong>{data.overview.inventory_quantity.toLocaleString("zh-CN")}</strong></div></div><div className="structure-grid"><section><h3>品牌库存结构</h3>{data.overview.brand_structure.map(row => <div key={row.name}><span>{row.name}</span><i style={{ width: `${row.share * 100}%` }} /><b>{(row.share * 100).toFixed(1)}%</b></div>)}</section><section><h3>门店库存结构</h3>{data.overview.store_structure.map(row => <div key={row.name}><span>{row.name}</span><i style={{ width: `${row.share * 100}%` }} /><b>{(row.share * 100).toFixed(1)}%</b></div>)}</section></div></article>
      <article className="business-module"><div className="module-title"><span>02</span><div><h2>库存健康分析</h2><p>正常库存 · 高库存 · 滞销库存 · 缺货风险</p></div></div><div className="health-tabs">{(["正常库存", "高库存", "滞销库存", "缺货风险"] as const).map(name => <button className={healthFilter === name ? "is-active" : ""} type="button" key={name} onClick={() => setHealthFilter(name)}>{name}<b>{data.health[name].length}</b></button>)}</div><div className="product-table inventory-health-table"><div><b>SKU / 商品</b><b>品牌</b><b>金额</b><b>数量</b><b>风险等级</b><b>建议</b></div>{data.health[healthFilter].map(row => <div key={row.sku}><strong>{row.product_name}<small>{row.sku}</small></strong><span>{row.brand_name}</span><span>{amount(row.inventory_amount)}</span><span>{row.inventory_quantity}</span><em>{row.risk_level}</em><span>{row.recommendation}</span></div>)}</div>{!data.health[healthFilter].length && <p className="module-state">当前没有{healthFilter}商品</p>}</article>
      <article className="business-module"><div className="module-title"><span>03</span><div><h2>滞销库存分析</h2><p>最近销售与库龄驱动去化行动</p></div></div><div className="product-table slow-table"><div><b>商品</b><b>品牌</b><b>库存金额</b><b>库存数量</b><b>最近销售</b><b>库龄</b><b>建议动作</b></div>{data.slow_moving.map(row => <div key={row.sku}><strong>{row.product_name}<small>{row.sku}</small></strong><span>{row.brand_name}</span><span>{amount(row.inventory_amount)}</span><span>{row.inventory_quantity}</span><span>{row.last_sale_date || "无销售记录"}</span><span>{row.inventory_age_days === undefined || row.inventory_age_days === null ? "待补齐" : `${row.inventory_age_days} 天`}</span><span>{row.recommendation}</span></div>)}</div>{!data.slow_moving.length && <p className="module-state">当前没有滞销库存</p>}</article>
      <article className="business-module"><div className="module-title"><span>04</span><div><h2>补货建议</h2><p>基于销售速度 · 库存 · 趋势</p></div></div><div className="advice-grid">{data.replenishment_recommendations.length ? data.replenishment_recommendations.map((row, index) => <div key={`${row.conclusion}-${index}`}><span>结论</span><p>{row.conclusion}</p><span>依据</span><p>{row.evidence}</p><span>建议</span><p>{row.recommendation}</p></div>) : <p className="module-state">当前没有补货风险建议</p>}</div></article>
    </>}
  </section>;
}


function CustomerIntelligence() {
  const [state, setState] = useState<LoadState<CustomerIntelligencePayload>>({ phase: "loading" });
  const load = async () => { setState({ phase: "loading" }); try { const response = await gatewayFetch("/api/business/customer-intelligence"); if (response.status === 401 || response.status === 403) return setState({ phase: "forbidden" }); if (!response.ok) return setState({ phase: "error" }); setState({ phase: "ready", data: await response.json() as CustomerIntelligencePayload }); } catch { setState({ phase: "error" }); } };
  useEffect(() => { void load(); }, []);
  const data = state.data; const text = state.phase === "loading" ? "正在读取 Customer360 数据…" : state.phase === "forbidden" ? "无权查看该经营范围" : state.phase === "error" ? "Customer360 数据暂不可用，请稍后重试" : "";
  const behavior = data?.purchase_behavior;
  const behaviorGroups = [{ title: "品牌偏好", rows: behavior?.brand_preferences.map(row => ({ ...row, value: row.preference })) }, { title: "品类偏好", rows: behavior?.category_preferences.map(row => ({ ...row, value: row.preference })) }, { title: "消费周期", rows: behavior?.purchase_cycles.map(row => ({ ...row, value: row.purchase_cycle })) }, { title: "购买趋势", rows: behavior?.purchase_trends.map(row => ({ ...row, value: row.purchase_trend })) }];
  return <section className="business-analysis customer-intelligence" id="customers" aria-labelledby="customer-title">
    <div className="analysis-hero business-hero"><div><p className="eyebrow">CUSTOMER INTELLIGENCE · V1.7</p><h1 id="customer-title">客户分析</h1><p>基于真实 Customer360 API，理解客户价值、购买行为与授权机会。</p></div><button type="button" onClick={() => void load()}>刷新数据</button></div>
    <Provenance payload={data} state={state.phase} />{state.phase !== "ready" && <p className="module-state">{text}</p>}
    {data && <>
      <article className="business-module"><div className="module-title"><span>01</span><div><h2>客户总览</h2><p>客户规模 · 活跃 · 消费 · 订单 · VIP</p></div></div><div className="business-metrics customer-metrics">{[["客户数量", data.overview.customer_count], ["活跃客户", data.overview.active_customers], ["消费金额", money(data.overview.consumption_amount)], ["订单数量", data.overview.order_count], ["平均消费", money(data.overview.average_consumption)], ["VIP数量", data.overview.vip_count]].map(([label,value]) => <div key={label}><span>{label}</span><strong>{typeof value === "number" ? value.toLocaleString("zh-CN") : value}</strong></div>)}</div></article>
      <article className="business-module"><div className="module-title"><span>02</span><div><h2>客户价值分层</h2><p>Customer360 返回的价值标签</p></div></div><div className="segment-grid">{data.value_segments.map(row => <div key={row.name}><span>{row.name}</span><strong>{row.count.toLocaleString("zh-CN")}</strong><small>位客户</small></div>)}</div></article>
      <article className="business-module"><div className="module-title"><span>03</span><div><h2>购买行为分析</h2><p>品牌偏好 · 品类偏好 · 消费周期 · 购买趋势</p></div></div><div className="behavior-grid">{behaviorGroups.map(group => <section key={group.title}><h3>{group.title}</h3>{group.rows?.length ? group.rows.map(row => <div key={`${row.customer_id}-${String(row.value)}`}><span>{row.customer_name}</span><b>{String(row.value)}</b></div>) : <p>Customer360 暂无返回数据</p>}</section>)}</div></article>
      <article className="business-module"><div className="module-title"><span>04</span><div><h2>客户机会池</h2><p>customer_opportunities · 复购 · 升级 · 召回 · 交叉销售</p></div></div><div className="product-table customer-opportunity-table"><div><b>客户</b><b>机会类型</b><b>原因</b><b>依据</b><b>建议动作</b><b>负责人</b></div>{data.customer_opportunities.map(row => <div key={`${row.customer_id}-${row.opportunity_type}`}><strong>{row.customer}<small>{row.customer_id}</small></strong><em>{row.opportunity_type}</em><span>{row.reason || pending}</span><span>{row.evidence || pending}</span><span>{row.recommended_action || pending}</span><span>{row.owner || pending}</span></div>)}</div>{!data.customer_opportunities.length && <p className="module-state">当前没有 Customer360 返回的客户机会</p>}<div className="wecom-reserved"><b>企业微信</b><span>接口已预留 · 未启用推送 · 不自动执行</span></div></article>
    </>}
  </section>;
}


function SupplyChainIntelligence() {
  const syncing = "供应链数据同步中。";
  const now = new Date();
  const [dateFrom, setDateFrom] = useState(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`);
  const [dateTo, setDateTo] = useState(`${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()).padStart(2, "0")}`);
  const [state, setState] = useState<LoadState<SupplyChainPayload>>({ phase: "loading" });
  const load = async () => { setState({ phase: "loading" }); try { const query = new URLSearchParams({ date_from: dateFrom, date_to: dateTo }); const response = await gatewayFetch(`/api/business/supply-chain-intelligence?${query}`); if (response.status === 401 || response.status === 403) return setState({ phase: "forbidden" }); if (!response.ok) return setState({ phase: "error" }); const payload = await response.json() as SupplyChainPayload; setState({ phase: payload.data_status?.status === "syncing" || !payload.overview ? "empty" : "ready", data: payload }); } catch { setState({ phase: "error" }); } };
  useEffect(() => { void load(); }, []);
  const data = state.data; const ready = state.phase === "ready" && data?.overview;
  const percent = (value: number | null | undefined) => numeric(value) ? `${(value * 100).toFixed(1)}%` : pending;
  const empty = (rows?: unknown[]) => !rows?.length ? <p className="module-state">{syncing}</p> : null;
  return <section className="business-analysis supply-chain-intelligence" id="supply-chain" aria-labelledby="supply-chain-title">
    <div className="analysis-hero business-hero"><div><p className="eyebrow">SUPPLY CHAIN INTELLIGENCE · V1.9</p><h1 id="supply-chain-title">供应链分析</h1><p>贯通供应商、品牌、采购、库存关联与交付风险，只读呈现真实供应链事实。</p></div><button type="button" onClick={() => void load()}>刷新数据</button></div>
    <div className="supply-toolbar"><label>开始日期<input type="date" value={dateFrom} onChange={event => setDateFrom(event.target.value)} /></label><label>结束日期<input type="date" value={dateTo} onChange={event => setDateTo(event.target.value)} /></label><button type="button" onClick={() => void load()}>应用范围</button><span>只读 · ALL DATA 授权范围</span></div>
    {data && <div className="analysis-provenance"><span><b>数据来源</b>{data.trace?.source_names?.join(" · ") || pending}</span><span><b>更新时间</b>{data.trace?.generated_at || pending}</span><span><b>数据状态</b>{data.data_status.status}</span></div>}
    {!ready ? <div className="supply-sync" role="status"><span>SYNC</span><div><strong>{state.phase === "forbidden" ? "无权查看该经营范围" : syncing}</strong><p>供应商、采购与库存关联数据就绪后将自动显示。</p></div></div> : <>
      <article className="business-module"><div className="module-title"><span>01</span><div><h2>供应链总览</h2><p>采购规模 · 收货进度 · 准时交付 · 未收数量</p></div></div><div className="business-metrics supply-overview">{[["供应商", data.overview!.supplier_count], ["采购单", data.overview!.purchase_order_count], ["采购金额", numeric(data.overview!.purchase_amount) ? money(data.overview!.purchase_amount) : pending], ["收货率", percent(data.overview!.receipt_rate)], ["准时率", percent(data.overview!.on_time_rate)], ["未收数量", metric(data.overview!.open_quantity ?? undefined)]].map(([label,value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div></article>
      <article className="business-module"><div className="module-title"><span>02</span><div><h2>供应商表现</h2><p>真实采购、收货与交付表现</p></div></div><div className="product-table supply-table supplier-performance"><div><b>供应商</b><b>采购单</b><b>采购金额</b><b>收货率</b><b>准时率</b><b>未收</b><b>最近采购</b></div>{data.supplier_performance.map(row => <div key={row.supplier_id}><strong>{row.supplier_name}<small>{row.supplier_id}</small></strong><span>{row.purchase_order_count}</span><span>{numeric(row.purchase_amount) ? money(row.purchase_amount) : pending}</span><span>{percent(row.receipt_rate)}</span><span>{percent(row.on_time_rate)}</span><span>{metric(row.open_quantity ?? undefined)}</span><span>{row.last_purchase_date}</span></div>)}</div>{empty(data.supplier_performance)}</article>
      <article className="business-module"><div className="module-title"><span>03</span><div><h2>品牌供应关系</h2><p>品牌与供应商显式关联，不推测缺失关系</p></div></div><div className="brand-supply-grid">{data.brand_supply_relationships.map(row => <section key={row.brand_id}><header><strong>{row.brand_name || pending}</strong><span>{row.brand_id}</span></header><p>{row.suppliers.map(item => item.supplier_name).join(" · ")}</p><dl><div><dt>供应商</dt><dd>{row.supplier_count}</dd></div><div><dt>采购数量</dt><dd>{metric(row.purchase_quantity)}</dd></div><div><dt>库存数量</dt><dd>{metric(row.inventory_quantity)}</dd></div></dl></section>)}</div>{empty(data.brand_supply_relationships)}</article>
      <article className="business-module"><div className="module-title"><span>04</span><div><h2>采购协同</h2><p>采购单、预计交付、实收与库存协同</p></div></div><div className="product-table supply-table procurement-table"><div><b>采购单 / SKU</b><b>供应商</b><b>品牌</b><b>订购 / 实收</b><b>预计 / 实际</b><b>未收</b><b>状态</b></div>{data.procurement_collaboration.map(row => <div key={`${row.purchase_document_ref}-${row.sku_id}`}><strong>{row.purchase_document_ref}<small>{row.sku_id}</small></strong><span>{row.supplier_name}</span><span>{row.brand_name || pending}</span><span>{metric(row.ordered_quantity)} / {metric(row.received_quantity ?? undefined)}</span><span>{row.expected_delivery_date || pending} / {row.received_date || pending}</span><span>{metric(row.open_quantity ?? undefined)}</span><em>{row.document_status}</em></div>)}</div>{empty(data.procurement_collaboration)}</article>
      <article className="business-module"><div className="module-title"><span>05</span><div><h2>供应链风险</h2><p>风险结论均保留采购事实依据</p></div></div><div className="supply-risk-list">{data.risks.map(row => <div key={row.risk_id}><span>!</span><div><strong>{row.risk_type === "late_delivery" ? "延迟交付" : row.risk_type === "overdue_delivery" ? "逾期未交" : row.risk_type}</strong><p>{row.conclusion}</p><small>{row.purchase_document_ref} · {row.sku_id}</small></div></div>)}</div>{empty(data.risks)}</article>
      <article className="business-module ai-advice"><div className="module-title"><span>AI</span><div><h2>AI建议</h2><p>仅展示 API 返回建议，不在前端生成判断</p></div></div>{data.ai_advice.items.length ? <div className="advice-grid">{data.ai_advice.items.map((item,index) => <div key={index}><span>结论</span><p>{item.conclusion || pending}</p><span>依据</span><p>{item.evidence?.join("；") || pending}</p><span>建议</span><p>{item.recommendation?.join("；") || pending}</p></div>)}</div> : <p className="module-state">{syncing}</p>}</article>
    </>}
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
    {activeSection === "products" && <ProductIntelligence />}
    {activeSection === "inventory" && <InventoryIntelligence />}
    {activeSection === "customers" && <CustomerIntelligence />}
    {activeSection === "organization" && <PeopleIntelligence />}
    {activeSection === "supply-chain" && <SupplyChainIntelligence />}


    {activeSection === "advisor" && <AIAdvisor />}
    <footer className="page-footer"><span>VAFOX CEO Portal · huyan.vafox.com</span><span>董事、CEO 与授权管理层专用 · 页面只读</span></footer>
    </main>
  </div>;
}
