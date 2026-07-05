# FoxBrain OS 1.0 Security Baseline

## Application Security

- HTTPS-only production access.
- HSTS response header.
- Content Security Policy.
- X-Frame-Options clickjacking protection.
- X-Content-Type-Options MIME sniffing protection.
- Referrer-Policy.
- Permissions-Policy for browser capability restriction.
- No-store cache policy for pages, JSON and file downloads.

## Identity and Access

- Session cookie is signed.
- Cookie uses `HttpOnly`, `Secure` and `SameSite=Lax`.
- Passwords are stored as salted hashes.
- Login failure lockout: 5 failures lock for 15 minutes.
- New users remain pending until admin approval.
- RBAC default deny.

## Governance

- Audit log records system and user actions.
- High-risk AI, automation and business actions require approval.
- SAP write-back, finance, price, contract and external publishing actions are approval-only.
- Secrets stay in server-only `.env` or `portal.env`.

## Server Baseline

- Public ports should be limited to 80 and 443.
- SSH should be restricted to administrators.
- Root login should be disabled when practical.
- Fail2ban or equivalent login protection should be enabled.
- Backups should be scheduled and restore-tested.
- SAP sync credentials must remain only on the server.

## Verification

- `/api/security/baseline`
- `/api/security/framework`
- `/api/health`
- `/api/product/release-1-0`

