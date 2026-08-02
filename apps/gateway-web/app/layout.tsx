import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VAFOX 户外生命生态",
  description: "VAFOX 户外生命生态统一身份与产品入口",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "VAFOX 户外生命生态" },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#f4f8f5" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="zh-CN"><body>{children}<script src="/register-sw.js" defer /></body></html>; }
