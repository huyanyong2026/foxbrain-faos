import type { NextConfig } from "next";
const nextConfig: NextConfig = { transpilePackages: ["@foxbrain/api-client", "@foxbrain/types"] };
export default nextConfig;
