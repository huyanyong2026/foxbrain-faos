import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CEO Today | VAFOX",
  description: "VAFOX CEO Today 今日经营驾驶舱",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "虎眼" },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#f6f6f4" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}<script src="/register-sw.js" defer /></body></html>; }
