"use client";
import { useState } from "react";
import type { RbacRole, WorkspaceDestination } from "@foxbrain/types";

const portals: { name: string; destination: WorkspaceDestination; roles: RbacRole[]; href: string; description: string }[] = [
  { name: "Outdoor LIFE", destination: "outdoor", roles: ["employee", "ceo"], href: "https://outdoor.vafox.com", description: "探索、装备与户外生活方式" },
  { name: "FoxBrain", destination: "ai", roles: ["employee", "ceo", "admin"], href: "https://ai.vafox.com", description: "每位员工的 AI 工作操作系统" },
  { name: "Huyan Intelligence", destination: "huyan", roles: ["ceo"], href: "https://huyan.vafox.com", description: "CEO 的实时经营智能中心" },
  { name: "Control", destination: "control", roles: ["admin"], href: "https://control.vafox.com", description: "组织、权限与运行控制平面" },
];
export default function GatewayPage() {
  const [role, setRole] = useState<RbacRole>("employee");
  const [message, setMessage] = useState("选择身份后，由 Gateway 验证可访问的 VAFOX 宇宙入口。");
  function enter(portal: typeof portals[number]) {
    if (!portal.roles.includes(role)) return setMessage(`${portal.name} 需要 ${portal.roles.join(" / ")} 权限；RBAC 已阻止此次跳转。`);
    setMessage(`身份已确认：${role}。生产环境将通过 Identity Gateway 跳转至 ${portal.href}。`);
  }
  return <main className="portal"><header><a className="brand" href="#top">VAFOX <span>OUTDOOR LIFE OS</span></a><span className="online">● GATEWAY / ONLINE</span></header><section id="top" className="portal-hero"><div><p className="eyebrow">NATURE × INTELLIGENCE</p><h1>VAFOX<br/><i>OUTDOOR LIFE OS</i></h1><p>一个以自然为灵感、以智能为驱动的户外生活宇宙。统一身份、安全网关和可解释的 AI 决策，让每一次探索与经营都连接起来。</p></div><aside><p className="eyebrow">IDENTITY CONTEXT</p><strong>VAFOX China</strong><span>选择当前角色，预览 RBAC 授权入口。</span><div className="role-switch" aria-label="身份角色">{(["employee", "ceo", "admin"] as RbacRole[]).map(value => <button className={role === value ? "selected" : ""} key={value} onClick={() => setRole(value)}>{value}</button>)}</div></aside></section><section><div className="section-title"><p className="eyebrow">UNIVERSE PORTAL</p><h2>从你的权限范围开始</h2></div><div className="portal-grid">{portals.map((portal, index) => <button className="portal-card" key={portal.destination} onClick={() => enter(portal)}><span>0{index + 1}</span><h2>{portal.name}</h2><p>{portal.description}</p><small>{portal.roles.join(" · ")} →</small></button>)}</div></section><p className="portal-notice" aria-live="polite">{message}</p></main>;
}
