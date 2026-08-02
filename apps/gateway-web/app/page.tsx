"use client";
import { useState } from "react";
import type { RbacRole, WorkspaceDestination } from "@foxbrain/types";

const portals: { name: string; displayName: string; destination: WorkspaceDestination; roles: RbacRole[]; href: string; description: string }[] = [
  { name: "户外生命生态", displayName: "户外生命生态", destination: "outdoor", roles: ["employee", "ceo"], href: "https://outdoor.vafox.com", description: "连接自然探索、专业装备与户外生活方式" },
  { name: "FoxBrain企业智能", displayName: "FoxBrain企业智能", destination: "ai", roles: ["employee", "ceo", "admin"], href: "https://ai.vafox.com", description: "面向每位员工的企业智能工作台" },
  { name: "Huyan智能经营中心", displayName: "Huyan智能经营中心", destination: "huyan", roles: ["ceo"], href: "https://huyan.vafox.com", description: "面向管理者的实时经营分析与决策支持" },
  { name: "控制中心", displayName: "控制中心", destination: "control", roles: ["admin"], href: "https://control.vafox.com", description: "组织、权限与运行的统一管理中心" },
];
export default function GatewayPage() {
  const [role, setRole] = useState<RbacRole>("employee");
  const [message, setMessage] = useState("选择身份后，由 Gateway 验证可访问的 VAFOX 宇宙入口。");
  function enter(portal: typeof portals[number]) {
    if (!portal.roles.includes(role)) return setMessage(`${portal.name} 需要 ${portal.roles.join(" / ")} 权限；RBAC 已阻止此次跳转。`);
    setMessage(`身份已确认：${role}。生产环境将通过 Identity Gateway 跳转至 ${portal.href}。`);
  }
  return <main className="portal"><header><a className="brand" href="#top">VAFOX <span>户外生命生态</span></a><span className="online">● 网关在线</span></header><section id="top" className="portal-hero"><div><p className="eyebrow">自然 × 智能</p><h1>VAFOX<br/><i>户外生命生态</i></h1><p>以自然为灵感、以智能为驱动，连接探索、装备、员工协作与企业经营。统一身份、安全网关和可解释的 AI 决策，让每一次行动更有把握。</p></div><aside><p className="eyebrow">当前身份</p><strong>VAFOX 中国区</strong><span>选择当前角色，预览已授权的产品入口。</span><div className="role-switch" aria-label="身份角色">{(["employee", "ceo", "admin"] as RbacRole[]).map(value => <button className={role === value ? "selected" : ""} key={value} onClick={() => setRole(value)}>{value === "employee" ? "员工" : value === "ceo" ? "经营负责人" : "管理员"}</button>)}</div></aside></section><section><div className="section-title"><p className="eyebrow">产品入口</p><h2>从你的授权范围开始</h2></div><div className="portal-grid">{portals.map((portal, index) => <button className="portal-card" key={portal.destination} onClick={() => enter(portal)}><span>0{index + 1}</span><h2>{portal.displayName}</h2><p>{portal.description}</p><small>{portal.roles.join(" · ")} →</small></button>)}</div></section><p className="portal-notice" aria-live="polite">{message}</p></main>;
}
