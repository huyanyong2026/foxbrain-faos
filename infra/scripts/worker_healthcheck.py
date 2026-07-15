"""Health check for the FoxBrain cloud worker container.

The worker does not expose an HTTP port. Docker therefore must not inherit the
application image HTTP health check; instead, validate that the scheduler process
for ``infra/scripts/cloud_worker.py`` is alive and running in this container.
"""

from __future__ import annotations

from pathlib import Path


WORKER_SCRIPT = Path("infra/scripts/cloud_worker.py")
WORKER_SCRIPT_NAME = WORKER_SCRIPT.name
PROC_ROOT = Path("/proc")
RUNNING_STATES = {"R", "S", "D", "I"}
PYTHON_COMMANDS = {"python", "python3"}


def _cmdline_args(proc_dir: Path) -> list[str]:
    try:
        raw = (proc_dir / "cmdline").read_bytes()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return []
    return [part.decode("utf-8", errors="ignore") for part in raw.split(b"\x00") if part]


def _process_state(proc_dir: Path) -> str:
    try:
        stat = (proc_dir / "stat").read_text(encoding="utf-8", errors="ignore")
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return ""
    parts = stat.rsplit(")", 1)
    if len(parts) != 2:
        return ""
    fields = parts[1].strip().split()
    return fields[0] if fields else ""


def _is_python_command(command: str) -> bool:
    executable = Path(command).name
    return executable in PYTHON_COMMANDS or executable.startswith("python")


def _is_worker_script_arg(arg: str) -> bool:
    arg_path = Path(arg)
    if arg_path.name != WORKER_SCRIPT_NAME:
        return False
    return arg == str(WORKER_SCRIPT) or arg.endswith(f"/{WORKER_SCRIPT}")


def _is_worker_process(args: list[str]) -> bool:
    if len(args) < 2 or not _is_python_command(args[0]):
        return False
    return any(_is_worker_script_arg(arg) for arg in args[1:])


def worker_process_running() -> bool:
    current_pid = str(Path("/proc/self").resolve().name)
    for proc_dir in PROC_ROOT.iterdir():
        if not proc_dir.name.isdigit() or proc_dir.name == current_pid:
            continue
        if _process_state(proc_dir) not in RUNNING_STATES:
            continue
        if _is_worker_process(_cmdline_args(proc_dir)):
            return True
    return False


def main() -> int:
    return 0 if worker_process_running() else 1


if __name__ == "__main__":
    raise SystemExit(main())
