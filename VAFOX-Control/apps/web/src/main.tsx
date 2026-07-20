import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Result = {
  id: string; task_id: string; executor: string; result_type: string; summary: string;
  risk_level: "low" | "medium" | "high" | "critical"; approval_status: "review_pending" | "cto_approved";
  created_at: string;
};

const API_ROOT = import.meta.env.VITE_API_ROOT ?? "/api";
const labels: Record<Result["approval_status"], string> = {
  review_pending: "Review pending", cto_approved: "CTO approved",
};

function ReviewDashboard() {
  const [results, setResults] = useState<Result[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_ROOT}/results`).then(async response => {
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      return response.json() as Promise<Result[]>;
    }).then(setResults).catch(() => setError("Results are unavailable. Start the local Control API to review submissions."));
  }, []);

  const taskCount = new Set(results.map(result => result.task_id)).size;
  return <main className="dashboard">
    <header><p className="eyebrow">VAFOX AI TEAM MANAGEMENT CENTER</p><h1>CTO Review Dashboard</h1><p>Review submitted work before it becomes completed. This console never executes external agents.</p></header>
    <section className="metrics" aria-label="Review overview">
      <article><span>Tasks</span><strong>{taskCount}</strong></article>
      <article><span>Results</span><strong>{results.length}</strong></article>
      <article><span>Pending review</span><strong>{results.filter(item => item.approval_status === "review_pending").length}</strong></article>
    </section>
    {error && <p className="notice" role="alert">{error}</p>}
    <section className="review-list" aria-label="Submitted results">
      <div className="list-heading"><span>Task</span><span>Result</span><span>Risk</span><span>Approval</span></div>
      {results.map(result => <article className="review-row" key={result.id}>
        <span className="task-id" title={result.task_id}>{result.task_id}</span>
        <span><b>{result.executor} · {result.result_type}</b><small>{result.summary}</small></span>
        <span className={`badge risk-${result.risk_level}`}>{result.risk_level}</span>
        <span className={`badge ${result.approval_status}`}>{labels[result.approval_status]}</span>
      </article>)}
      {!error && results.length === 0 && <p className="empty">No submitted results are awaiting review.</p>}
    </section>
  </main>;
}

function App() {
  if (window.location.pathname === "/reviews") return <ReviewDashboard />;
  return <main><p className="eyebrow">CONTROL.VAFOX.COM · V1</p><h1>VAFOX Control Plane</h1><p>Open <a href="/reviews">/reviews</a> for the CTO review dashboard. No production connections or external agent execution are enabled.</p></main>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
