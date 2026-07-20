FROM node:22-alpine AS build

WORKDIR /app

COPY apps/web/package.json ./
RUN npm install --ignore-scripts

COPY apps/web ./
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY apps/web/nginx.conf /etc/nginx/nginx.conf

EXPOSE 3001

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD wget --quiet --spider http://127.0.0.1:3001/ || exit 1

CMD ["nginx", "-g", "daemon off;", "-c", "/etc/nginx/nginx.conf"]
