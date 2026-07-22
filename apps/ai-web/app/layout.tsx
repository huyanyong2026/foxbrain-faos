import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FoxBrain 智能工作台",
  description: "VAFOX 员工 AI 智能工作台",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "FoxBrain" },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#f4f8f5" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}<script src="/register-sw.js" defer /></body></html>; }
