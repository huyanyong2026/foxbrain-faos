# Docker build definitions

`frontend.Dockerfile` builds either supported Next.js application using `--build-arg APP=ai-web` or `--build-arg APP=huyan-web`. Frontends receive only `NEXT_PUBLIC_API_BASE_URL` and call the API Gateway.
