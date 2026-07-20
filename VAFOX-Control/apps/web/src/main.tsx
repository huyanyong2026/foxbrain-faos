import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const reviews = [
  { task: "TASK-2026-001", executor: "Codex", result: "PR #184 · Review dashboard", risk: "Medium", approval: "Pending review", tone: "medium" },
  { task: "TASK-2026-002", executor: "WorkBuddy", result: "Deployment report · staging", risk: "Low", approval: "Approved", tone: "low" },
  { task: "TASK-2026-003", executor: "Marvis", result: "Service status report", risk: "High", approval: "Pending review", tone: "high" },
];

function App() {
  return <main>
    <header><p className="eyebrow">CONTROL.VAFOX.COM · BUSINESS LAYER V1</p><h1>CTO Review Dashboard</h1><p className="intro">Review AI team deliverables, evidence, risk, and approval state in one management-only control surface.</p></header>
    <section className="metrics"><article><strong>03</strong><span>Reported results</span></article><article><strong>02</strong><span>Pending CTO review</span></article><article><strong>01</strong><span>Approved records</span></article></section>
    <section className="panel"><div className="panel-heading"><div><p className="section-label">REVIEW QUEUE</p><h2>Submitted work</h2></div><span className="management">Management only · no agent dispatch</span></div>
      <div className="table" role="table"><div className="row table-head" role="row"><span>Task</span><span>Executor</span><span>Result</span><span>Risk</span><span>Approval</span></div>{reviews.map(review => <div className="row" role="row" key={review.task}><strong>{review.task}</strong><span>{review.executor}</span><span>{review.result}</span><span><i className={`badge ${review.tone}`}>{review.risk}</i></span><span className="approval">{review.approval}</span></div>)}</div>
    </section>
    <section className="flow"><p className="section-label">FUTURE DISPATCHER DESIGN</p><div><b>Task</b><em>→</em><b>Executor</b><em>→</em><b>Result</b></div><p>Codex · WorkBuddy · Marvis are managed as declared executors. This phase records and reviews results; it does not call external agents.</p></section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
