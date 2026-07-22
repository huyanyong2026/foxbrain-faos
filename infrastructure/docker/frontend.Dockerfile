FROM node:22-alpine AS build
WORKDIR /app
ARG APP
COPY package.json ./
COPY packages ./packages
COPY apps/${APP}/package.json ./apps/${APP}/package.json
RUN npm install --no-audit --no-fund
COPY apps/${APP} ./apps/${APP}
RUN npm run build --workspace=@foxbrain/${APP}

FROM node:22-alpine
WORKDIR /app
ARG APP
ENV NODE_ENV=production
COPY --from=build /app /app
EXPOSE 3000
CMD ["sh", "-c", "npm run start --workspace=@foxbrain/${APP}"]
