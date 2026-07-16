# Runtime Health Guide

Run deterministic CI checks:

```bash
PYTHONPATH=. python automation_health_check.py
```

Run live runtime probes:

```bash
FOXBRAIN_HEALTH_LIVE=1 FOXBRAIN_HEALTH_TOKEN=<token> PYTHONPATH=. python automation_health_check.py
```

PASS requires Gateway, Huyan, AI, Core, Data Chain, Automation, and Version checks to pass.
