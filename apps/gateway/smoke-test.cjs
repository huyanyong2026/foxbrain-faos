const baseUrl = (process.env.GATEWAY_URL || "http://127.0.0.1:4173/").replace(/\/$/, "");

const requiredContent = [
  "火狐狸",
  "共同分享生命的体验与快乐",
  "为每一次出行，提供高品质、安全、实用、美学的户外产品与服务。",
  "开始探索",
  "发现装备",
  "了解火狐狸",
  "润物细无声",
];
const forbiddenContent = ["大道至简", "Brand Universe", "Dream Community"];
const assets = [
  "/assets/styles.css",
  "/assets/images/gateway-hero.webp",
];

(async () => {
  const page = await fetch(`${baseUrl}/`);
  if (!page.ok) throw new Error(`首页返回 ${page.status}`);
  const html = await page.text();
  const missing = requiredContent.filter((text) => !html.includes(text));
  if (missing.length) throw new Error(`首页缺少内容：${missing.join("、")}`);
  const forbidden = forbiddenContent.filter((text) => html.includes(text));
  if (forbidden.length) throw new Error(`首页仍有应移除内容：${forbidden.join("、")}`);

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
