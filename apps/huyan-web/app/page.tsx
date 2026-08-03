"use client";

import { useEffect, useState } from "react";
import { gatewayFetch } from "@foxbrain/api-client";

type Dashboard = {
  ai_summary: string;
  sales: number;
  orders: number;
  operating_stores: { store_code: string; store_name: string; status: string }[];
  top_brands: { brand_name: string; sales: number }[];
  risks: { type: string; title: string; severity: string; message: string }[];
  effective_skus: number;
  customer_opportunities: { title: string; reason: string }[];
  ai_recommendations: string[];
  data_source: string;
  updated_at: string;
  confidence: number | string;
};

const navItems = [["CEO Today", "today"], ["经营分析", "operations"], ["商品分析", "products"], ["库存分析", "inventory"], ["客户分析", "customers"], ["组织分析", "organization"], ["供应链分析", "supply-chain"], ["AI顾问", "advisor"]];

const money = (value: number) =>
  new Intl.NumberFormat("zh-CN", {
    style: "currency",
    currency: "CNY",
    maximumFractionDigits: 0,
  }).format(value);

const statusLabel = (status: string) => status === "ACTIVE" ? "正常营业" : status;
const unavailable = "数据暂不可用";
const activeStores = ["zhenxing", "nanshan", "hangyuan", "jinsha", "online"];

export default function HuyanPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [status, setStatus] = useState("正在同步经营数据");
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    gatewayFetch("/api/ceo/today")
      .then(async (response) => {
        if (!response.ok) throw new Error(String(response.status));
        const report = await response.json() as Dashboard;
        if (![report.sales, report.orders, report.effective_skus].every(Number.isFinite) || !report.data_source || !report.updated_at) throw new Error("invalid_ceo_api_payload");
        setData(report);
        setStatus("数据已更新");
      })
      .catch(() => { setFailed(true); setStatus(unavailable); });
  }, []);

  const metrics = [
    { label: "今日销售额", value: failed ? unavailable : data ? money(data.sales) : "—", note: "sales · 五店合计", tone: "primary" },
    { label: "今日订单", value: failed ? unavailable : data?.orders ?? "—", suffix: data ? " 单" : "", note: "orders" },
    { label: "客单价", value: failed ? unavailable : data && data.orders > 0 ? money(data.sales / data.orders) : "—", note: "sales / orders" },
    { label: "有效库存 SKU", value: failed ? unavailable : data?.effective_skus ?? "—", note: "effective_skus" },
    { label: "客户机会", value: failed ? unavailable : data?.customer_opportunities.length ?? "—", suffix: data ? " 条" : "", note: "customer_opportunities" },
    { label: "数据状态", value: failed ? unavailable : data ? "已更新" : "同步中", note: data ? `可信度 ${data.confidence}` : "等待 CEO API", tone: "status" },
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
          {failed ? <p className="empty-state">{unavailable}</p> : data?.operating_stores.filter((store) => activeStores.includes(store.store_code)).sort((a, b) => activeStores.indexOf(a.store_code) - activeStores.indexOf(b.store_code)).map((store) => <article key={store.store_code}><span className="store-icon">店</span><div><strong>{store.store_name}</strong><small><i />{statusLabel(store.status)}</small></div><b>›</b></article>) ?? <p className="empty-state">正在读取门店状态…</p>}
        </div>
      </section>

      <section className="insight-grid" id="advisor">
        <article className="ai-summary">
          <div className="panel-kicker"><span className="ai-icon">AI</span><div><p>AI 经营摘要</p><small>基于当前可信数据生成</small></div></div>
          <blockquote>{failed ? unavailable : data?.ai_summary ?? "正在读取经营摘要…"}</blockquote>
          <div className="recommendations"><span>今日建议</span>{failed ? <p className="empty-state">{unavailable}</p> : <ol>{data?.ai_recommendations.slice(0, 3).map((item) => <li key={item}>{item}</li>)}</ol>}</div>
          <footer><span>数据来源</span><strong>{failed ? unavailable : data?.data_source ?? "CEO API"}</strong></footer>
        </article>

        <article className="risk-panel" id="inventory">
          <div className="section-title compact"><div><p className="eyebrow">RISK ALERT</p><h2>风险预警</h2></div><span className="risk-count">{data?.risks.length ?? 0}</span></div>
          <div className="risk-list">
            {failed ? <p className="empty-state">{unavailable}</p> : data?.risks.slice(0, 4).map((risk) => <div className="risk-item" key={`${risk.type}-${risk.title}`}><span>!</span><div><strong>{risk.title}</strong><p>{risk.message}</p></div><small>{risk.severity}</small></div>) ?? <p className="empty-state">正在读取风险数据…</p>}
            {data && data.risks.length === 0 && <p className="empty-state">当前没有需要处理的风险。</p>}
          </div>
        </article>
      </section>

      <section className="bottom-grid">
        <article className="table-panel" id="products">
          <div className="section-title compact"><div><p className="eyebrow">BRAND SALES</p><h2>TOP 品牌销售</h2></div><span className="period">今日</span></div>
          <div className="brand-list">
            {data?.top_brands.slice(0, 5).map((brand, index) => {
              const max = Math.max(...data.top_brands.map((item) => item.sales), 1);
              return <div className="brand-row" key={brand.brand_name}><b>{String(index + 1).padStart(2, "0")}</b><div><span><strong>{brand.brand_name}</strong><small>{money(brand.sales)}</small></span><i><em style={{ width: `${Math.max(8, brand.sales / max * 100)}%` }} /></i></div></div>;
            }) ?? <p className="empty-state">{failed ? unavailable : "正在读取品牌销售…"}</p>}
          </div>
        </article>

        <article className="table-panel" id="customers">
          <div className="section-title compact"><div><p className="eyebrow">CUSTOMER ONLY</p><h2>客户机会 TOP5</h2></div><span className="customer-only">客户与供应商已分离</span></div>
          <div className="opportunity-list">
            {data?.customer_opportunities.slice(0, 5).map((item, index) => <div className="opportunity-row" key={`${item.title}-${index}`}><b>{index + 1}</b><div><strong>{item.title}</strong><p>{item.reason}</p></div><span>待跟进</span></div>) ?? <p className="empty-state">{failed ? unavailable : "正在读取客户机会…"}</p>}
            {data && data.customer_opportunities.length === 0 && <p className="empty-state">当前暂无已授权客户机会。</p>}
          </div>
        </article>
      </section>

      <section className="data-provenance" aria-label="数据状态"><span><b>data_source</b>{failed ? unavailable : data?.data_source ?? "—"}</span><span><b>updated_at</b>{failed ? unavailable : data?.updated_at ?? "—"}</span><span><b>confidence</b>{failed ? unavailable : data?.confidence ?? "—"}</span></section>

      <footer className="page-footer"><span>VAFOX CEO Today</span><span>HISTORY SKU 不进入默认库存统计 · 页面只读</span></footer>
    </main>
  );
}
