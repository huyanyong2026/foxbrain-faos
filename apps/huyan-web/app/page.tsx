"use client";

import { useEffect, useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";

type Dashboard = {
  trust_status: string;
  ai_summary: string;
  sales_summary: { amount: number; source: string };
  operating_stores: { id: string; name: string; status: string }[];
  top_brands: { brand: string; sales: number }[];
  inventory_risks: { type: string; product: string; severity: string; message: string }[];
  inventory_validation: { effective_skus: number; history_skus: number };
  customer_opportunities: { title: string; reason: string }[];
  ai_recommendations: string[];
  cost_governance: { brand: string; sku: string; sales: number; gross_margin_rate: number | null; cost_status: string }[];
  employee_attribution: { sales_rows: number; attributed_rows: number; pending_rows: number };
  customer360: { profiles: number; purchase_profiles: number; wecom_bound_profiles: number; fusion_status: string };
  suppliers: { status: string; write_enabled: boolean };
};

const navItems = [["CEO Today", "today"], ["经营分析", "operations"], ["商品分析", "products"], ["库存分析", "inventory"], ["客户分析", "customers"], ["组织分析", "organization"], ["供应链分析", "supply-chain"], ["AI顾问", "advisor"]];

const money = (value: number) =>
  new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 0,
  }).format(value);

const statusLabel = (status: string) => status === "ACTIVE" ? "正常营业" : status;

export default function HuyanPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [status, setStatus] = useState("正在同步经营数据");

  useEffect(() => {
    gatewayFetch("/api/ceo/daily-report")
      .then(async (response) => {
        if (!response.ok) throw new Error(String(response.status));
        const report = await response.json() as { business: Dashboard };
        setData(report.business);
        setStatus(report.business.trust_status === "CEO_Dashboard_Data_Trusted_Complete" ? "数据已更新" : "数据待复核");
      })
      .catch(() => setStatus("数据服务暂不可用"));
  }, []);

  const metrics = [
    { label: "今日销售额", value: data ? money(data.sales_summary.amount) : "—", note: "五店合计", tone: "primary" },
    { label: "经营门店", value: data?.operating_stores.length ?? "—", suffix: data ? " 家" : "", note: "含网店" },
    { label: "有效库存 SKU", value: data?.inventory_validation.effective_skus ?? "—", note: "已排除 HISTORY SKU" },
    { label: "库存风险", value: data?.inventory_risks.length ?? "—", suffix: data ? " 项" : "", note: "待人工复核", tone: data?.inventory_risks.length ? "warning" : "" },
    { label: "客户机会", value: data?.customer_opportunities.length ?? "—", suffix: data ? " 条" : "", note: "客户独立口径" },
    { label: "数据状态", value: data ? "可信" : "同步中", note: data ? "只读数据链完整" : "等待 CEO API", tone: "status" },
  ];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark">V</span><strong>VAFOX</strong><span className="brand-divider" /><span>CEO Today</span></div>
        <div className="header-meta"><span className={`data-state ${data ? "is-live" : ""}`}><i />{status}</span><span className="today">今日经营</span><span className="avatar">CEO</span></div>
      </header>

      <nav className="primary-nav" aria-label="CEO OS 主导航">
        {navItems.map(([label, anchor]) => <a href={`#${anchor}`} key={anchor}>{label}</a>)}
      </nav>

      <section className="welcome" id="today" aria-labelledby="page-title">
        <div><p className="eyebrow">CEO TODAY · V6.1.11.3</p><h1 id="page-title">早上好，呼总</h1><p>今天的经营重点与需要关注的事项，已为您汇总。</p></div>
        <div className="scope"><span>经营范围</span><strong>振兴 · 南山 · 航苑 · 金沙 · 网店</strong><small>历史店已排除</small></div>
      </section>

      <section className="metrics-grid" id="operations" aria-label="六个核心经营指标">
        {metrics.map((metric) => <article className={`metric-card ${metric.tone ?? ""}`} key={metric.label}>
          <div className="metric-head"><span>{metric.label}</span><i>↗</i></div>
          <strong>{metric.value}<small>{metric.suffix}</small></strong>
          <p>{metric.note}</p>
        </article>)}
      </section>

      <section className="section-block" id="organization">
        <div className="section-title"><div><p className="eyebrow">STORE STATUS</p><h2>五店经营状态</h2></div><span className="quiet-badge">仅当前经营主体</span></div>
        <div className="store-grid">
          {data?.operating_stores.map((store) => <article key={store.id}><span className="store-icon">店</span><div><strong>{store.name}</strong><small><i />{statusLabel(store.status)}</small></div><b>›</b></article>) ?? <p className="empty-state">正在读取门店状态…</p>}
        </div>
      </section>

      <section className="insight-grid" id="advisor">
        <article className="ai-summary">
          <div className="panel-kicker"><span className="ai-icon">AI</span><div><p>AI 经营摘要</p><small>基于当前可信数据生成</small></div></div>
          <blockquote>{data?.ai_summary ?? "等待 CEO API 返回已验证数据，当前不展示推测值。"}</blockquote>
          <div className="recommendations"><span>今日建议</span><ol>{(data?.ai_recommendations ?? ["数据同步后生成经营建议。"] as string[]).slice(0, 3).map((item) => <li key={item}>{item}</li>)}</ol></div>
          <footer><span>数据来源</span><strong>{data?.sales_summary.source ?? "SAP B1 → Mirror → Data Core → CEO API"}</strong></footer>
        </article>

        <article className="risk-panel" id="inventory">
          <div className="section-title compact"><div><p className="eyebrow">RISK ALERT</p><h2>风险预警</h2></div><span className="risk-count">{data?.inventory_risks.length ?? 0}</span></div>
          <div className="risk-list">
            {data?.inventory_risks.slice(0, 4).map((risk) => <div className="risk-item" key={`${risk.type}-${risk.product}`}><span>!</span><div><strong>{risk.product}</strong><p>{risk.message}</p></div><small>{risk.severity}</small></div>) ?? <p className="empty-state">正在读取风险数据…</p>}
            {data && data.inventory_risks.length === 0 && <p className="empty-state">当前没有需要处理的库存风险。</p>}
          </div>
        </article>
      </section>

      <section className="bottom-grid">
        <article className="table-panel" id="products">
          <div className="section-title compact"><div><p className="eyebrow">BRAND SALES</p><h2>TOP 品牌销售</h2></div><span className="period">今日</span></div>
          <div className="brand-list">
            {data?.top_brands.slice(0, 5).map((brand, index) => {
              const max = Math.max(...data.top_brands.map((item) => item.sales), 1);
              return <div className="brand-row" key={brand.brand}><b>{String(index + 1).padStart(2, "0")}</b><div><span><strong>{brand.brand}</strong><small>{money(brand.sales)}</small></span><i><em style={{ width: `${Math.max(8, brand.sales / max * 100)}%` }} /></i></div></div>;
            }) ?? <p className="empty-state">正在读取品牌销售…</p>}
          </div>
        </article>

        <article className="table-panel" id="customers">
          <div className="section-title compact"><div><p className="eyebrow">CUSTOMER ONLY</p><h2>客户机会 TOP5</h2></div><span className="customer-only">客户与供应商已分离</span></div>
          <div className="opportunity-list">
            {data?.customer_opportunities.slice(0, 5).map((item, index) => <div className="opportunity-row" key={`${item.title}-${index}`}><b>{index + 1}</b><div><strong>{item.title}</strong><p>{item.reason}</p></div><span>待跟进</span></div>) ?? <p className="empty-state">正在读取客户机会…</p>}
            {data && data.customer_opportunities.length === 0 && <p className="empty-state">当前暂无已授权客户机会。</p>}
          </div>
        </article>
      </section>

      <section className="readiness-grid" aria-label="每日使用数据治理状态">
        <article><p className="eyebrow">COST GOVERNANCE</p><h2>成本治理 · TOP SKU</h2><strong>{data?.cost_governance.filter((item) => item.cost_status === "complete").length ?? "—"} <small>条成本已完整</small></strong><p>{data?.cost_governance[0] ? `${data.cost_governance[0].brand} · ${data.cost_governance[0].sku} · 毛利率 ${((data.cost_governance[0].gross_margin_rate ?? 0) * 100).toFixed(1)}%` : "正在读取品牌与 SKU 成本…"}</p></article>
        <article><p className="eyebrow">EMPLOYEE SALES</p><h2>员工销售归属</h2><strong>{data ? `${data.employee_attribution.attributed_rows}/${data.employee_attribution.sales_rows}` : "—"} <small>笔已归属</small></strong><p>{data?.employee_attribution.pending_rows ? `仍有 ${data.employee_attribution.pending_rows} 笔待补齐，优先核实网店归属。` : "销售归属已完整。"}</p></article>
        <article><p className="eyebrow">CUSTOMER 360</p><h2>客户企微融合</h2><strong>{data?.customer360.profiles ?? "—"} <small>个客户档案</small></strong><p>{data?.customer360.wecom_bound_profiles ? `已授权融合 ${data.customer360.wecom_bound_profiles} 个企微档案。` : "等待已授权企微身份绑定，不推测客户关系。"}</p></article>
        <article id="supply-chain"><p className="eyebrow">SUPPLY CHAIN</p><h2>供应商与供应链</h2><strong>{data?.suppliers.status === "available_via_data_core" ? "可查询" : "—"} <small>Data Core 只读</small></strong><p>供应商、采购与库存风险保持原有口径；不创建采购单。</p></article>
      </section>

      <footer className="page-footer"><span>VAFOX CEO Today</span><span>HISTORY SKU 不进入默认库存统计 · 页面只读</span></footer>
    </main>
  );
}
