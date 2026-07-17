const baseUrl = (process.env.GATEWAY_URL || "http://127.0.0.1:4173/").replace(/\/$/, "");

const requiredContent = [
  "欢迎回家",
  "VAFOX Identity Center",
  "VAFOX Story",
  "Adventure",
  "Brand Universe",
  "Explorer",
  "/explorer/register",
  "南山店",
  "commerce.vafox.com",
  "ai.vafox.com",
];
const assets = [
  "/assets/styles.css",
  "/assets/app.js",
  "/assets/images/gateway-hero.webp",
  "/assets/images/adventure-lake.webp",
  "/assets/images/firefox-store.webp",
  "/assets/images/vafox-logo.png",
];

(async () => {
  const page = await fetch(`${baseUrl}/`);
  if (!page.ok) throw new Error(`首页返回 ${page.status}`);
  const html = await page.text();
  const missing = requiredContent.filter((text) => !html.includes(text));
  if (missing.length) throw new Error(`首页缺少内容：${missing.join("、")}`);

  const assetResults = await Promise.all(assets.map(async (path) => {
    const response = await fetch(`${baseUrl}${path}`);
    return { path, status: response.status, bytes: Number(response.headers.get("content-length") || 0) };
  }));
  const failedAssets = assetResults.filter((asset) => asset.status !== 200);
  if (failedAssets.length) throw new Error(`资源加载失败：${failedAssets.map((asset) => asset.path).join("、")}`);

  console.log(JSON.stringify({ status: "通过", pageStatus: page.status, assetResults }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
