# Sprint019.1 Route Performance Report

## Baseline Before Upgrade

Measured from the production server through HTTPS with an authenticated session:

| Route | Status | Total Time | Size |
|---|---:|---:|---:|
| `/` | 200 | 0.156s | 13.0KB |
| `/ceo-workbench` | 200 | 0.144s | 19.0KB |
| `/copilot` | 200 | 0.232s | 11.6KB |
| `/daily-intelligence` | 200 | 0.019s | 12.2KB |
| `/decision` | 200 | 0.022s | 19.1KB |
| `/inventory-intelligence` | 200 | 0.094s | 20.4KB |
| `/brand-intelligence` | 200 | 0.020s | 13.1KB |
| `/store-intelligence` | 200 | 0.020s | 12.6KB |
| `/business-health` | 200 | 0.018s | 11.4KB |

## Interpretation

Server response time was already acceptable. Sprint019.1 focuses on perceived performance: fewer first-level choices, compact homepage, persistent Copilot, clearer empty states, and duplicate-click prevention.

## Post-Deployment

Measured after deployment:

| Route | Status | Total Time | Size |
|---|---:|---:|---:|
| `/` | 200 | 0.210s | 15.0KB |
| `/ceo-workbench` | 200 | 0.327s | 20.9KB |
| `/copilot` | 200 | 0.017s | 13.6KB |
| `/daily-intelligence` | 200 | 0.019s | 14.6KB |
| `/decision` | 200 | 0.024s | 21.1KB |
| `/business-health` | 200 | 0.018s | 13.4KB |
| `/inventory-intelligence` | 200 | 0.094s | 22.4KB |
| `/brand-intelligence` | 200 | 0.021s | 15.1KB |
| `/store-intelligence` | 200 | 0.019s | 14.6KB |
| `/action-center` | 200 | 0.147s | 15.4KB |

Homepage remains under the 2-second first meaningful render target in production route testing.
