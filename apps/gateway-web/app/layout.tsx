import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VAFOX 统一入口",
  description: "VAFOX 中国区统一身份与工作入口",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "VAFOX" },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#f4f8f5" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}<script src="/register-sw.js" defer /></body></html>; }
