# 10 API Standard / API 规范

## 当前 API

- `GET /api/dashboard/summary`
- `GET /api/sap/business-analysis`
- `GET /api/sap/profit-analysis`
- `GET /api/sap/inventory-analysis`
- `GET /api/sap/sales-trend`
- `GET /api/sap/ai-analysis`

## 设计原则

- 返回 JSON。
- 不暴露密码。
- 错误信息可读。
- 所有写操作需要登录。
- 后续增加 token/API key 鉴权。

## 推荐返回结构

```json
{
  "ok": true,
  "data": {},
  "message": ""
}
```

