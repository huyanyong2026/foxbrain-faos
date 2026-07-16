#!/usr/bin/env python3
"""Deployment protection for FoxBrain AI Workforce V5."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
workbench = (ROOT / "apps/ai/templates/workbench.html").read_text(encoding="utf-8")
base = (ROOT / "apps/ai/templates/base.html").read_text(encoding="utf-8")
app = (ROOT / "apps/ai/app.py").read_text(encoding="utf-8")
checks = {
    "frontend version badge": "FoxBrain AI Workforce V5" in workbench and "runtime_version.commit" in workbench,
    "ai router enabled": "data-ai-router-v5=\"enabled\"" in workbench and "route_intent" in app,
    "core connection": "core.vafox.com" in app and "read_only_auto_linked" in app,
    "no legacy UI": all(text not in workbench for text in ("选择助手", "关联对象类型", "关联对象<input", "本次分析依据", "提交分析")),
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + " " + name)
if not all(checks.values()):
    sys.exit(1)
