"""Health check for the FoxBrain cloud worker container.

The worker does not expose an HTTP port. Docker therefore must not inherit the
application image HTTP health check; instead, validate that the scheduler process
is still running in this container.
"""

from __future__ import annotations

from pathlib import Path


WORKER_SCRIPT = "infra/scripts/cloud_worker.py"
PROC_ROOT = Path("/proc")


def _cmdline_args(proc_dir: Path) -> list[str]:
    try:
        raw = (proc_dir / "cmdline").read_bytes()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return []
    return [part.decode("utf-8", errors="ignore") for part in raw.split(b"\x00") if part]


def _is_worker_process(args: list[str]) -> bool:
    if len(args) < 2:
        return False
    executable = Path(args[0]).name
    if not executable.startswith("python"):
        return False
    return any(arg == WORKER_SCRIPT or arg.endswith(f"/{WORKER_SCRIPT}") for arg in args[1:])


def worker_process_running() -> bool:
    current_pid = str(Path("/proc/self").resolve().name)
    for proc_dir in PROC_ROOT.iterdir():
        if not proc_dir.name.isdigit() or proc_dir.name == current_pid:
            continue
        if _is_worker_process(_cmdline_args(proc_dir)):
            return True
    return False


def main() -> int:
    return 0 if worker_process_running() else 1


if __name__ == "__main__":
    raise SystemExit(main())
