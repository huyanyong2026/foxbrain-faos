# AI OS V4 Deployment Guide

1. Build generates `deployment.json` with `scripts/generate_deployment_metadata.py`.
2. Deploy attaches the metadata file beside the services.
3. Services read metadata and expose it at `/health/version`.
4. Run `python verify_production.py` after deploy.
