import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const cards = ["Server Registry", "Service Registry", "Deployment Registry", "Health Checks"];
function App() { return <main><p className="eyebrow">CONTROL.VAFOX.COM · V1</p><h1>VAFOX Control Plane</h1><p>Architecture scaffold — no production connections enabled.</p><section>{cards.map(card => <article key={card}><h2>{card}</h2><p>Ready for the reviewed API integration phase.</p></article>)}</section></main>; }

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
