# FoxBrain Nginx Integration Report V1.0

## Scope

This change integrates FoxBrain FAOS with the existing production system Nginx on `140.143.207.194` for `huyan.vafox.com` without allowing the Docker Compose `foxbrain-nginx` container to bind the public HTTP/HTTPS ports already owned by the host Nginx.

## Current Architecture

Before this change, the Compose `nginx` service (`foxbrain-nginx`) attempted to publish public ports directly:

- `80:80`
- `443:443`

That conflicted with the production server's existing system Nginx, which already listens on ports `80` and `443` for existing virtual hosts, including but not limited to:

- `dify.huyan.vafox.com`
- `n8n.huyan.vafox.com`

The FoxBrain application services remain internal Docker services:

- `foxbrain-web` on container port `3000`
- `foxbrain-api` on container port `8000`
- `foxbrain-worker`
- `postgres`
- `redis`
- `minio`
- `qdrant`

## New Architecture

The production system Nginx remains the only service binding public ports `80` and `443` on the host.

The Compose `foxbrain-nginx` service no longer publishes `80:80` or `443:443`. Instead, it publishes its HTTP listener only on the host loopback interface using an approved local port:

- `127.0.0.1:${FOXBRAIN_NGINX_HOST_PORT:-8088}:80`

This avoids any conflict with system Nginx while preserving Docker-internal routing from `foxbrain-nginx` to:

- `foxbrain-web:3000`
- `foxbrain-api:8000`

System Nginx should then proxy only the `huyan.vafox.com` virtual host to the local FoxBrain proxy port. Existing `dify.huyan.vafox.com` and `n8n.huyan.vafox.com` server blocks must remain unchanged.

## Proxy Target

Recommended production target for the host Nginx `huyan.vafox.com` server block:

```nginx
proxy_pass http://127.0.0.1:8088;
```

If a different local port is required, set it before starting Compose:

```bash
export FOXBRAIN_NGINX_HOST_PORT=18088
docker compose up -d
```

Then update the host Nginx template to proxy to the same local port.

## Host Nginx Configuration Template

Use `infra/nginx/huyan.vafox.com.host-nginx.conf` as the production host Nginx template for `huyan.vafox.com`.

Installation outline on the production server:

```bash
sudo cp infra/nginx/huyan.vafox.com.host-nginx.conf /etc/nginx/conf.d/huyan.vafox.com.conf
sudo nginx -t
sudo systemctl reload nginx
```

Before installing, confirm there are no duplicate `server_name huyan.vafox.com;` blocks in other enabled Nginx files.

## Validation Plan

Run from the repository root on the production server:

```bash
docker compose config
docker compose up -d
docker compose ps
```

Expected service state:

- `foxbrain-web` is healthy
- `foxbrain-api` is healthy
- `foxbrain-worker` is running
- `foxbrain-nginx` is running and bound only to `127.0.0.1:${FOXBRAIN_NGINX_HOST_PORT:-8088}` on the host
- System Nginx continues to own public ports `80` and `443`

## Rollback Plan

If the integration fails:

1. Restore the previous host Nginx configuration for `huyan.vafox.com`.
2. Test and reload host Nginx:

   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. Stop or recreate only the FoxBrain proxy container if needed:

   ```bash
   docker compose stop nginx
   docker compose up -d nginx
   ```

4. Confirm existing virtual hosts are unaffected:

   ```bash
   curl -I https://dify.huyan.vafox.com
   curl -I https://n8n.huyan.vafox.com
   ```

This rollback does not require database changes and does not modify application, AI, or SAP logic.
