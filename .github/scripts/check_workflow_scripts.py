#!/usr/bin/env python3
"""Validate GitHub Actions deployment scripts before any SSH action runs."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
SCRIPT_START = re.compile(r"^(?P<indent>\s*)script:\s*\|\s*$")
GITHUB_EXPRESSION = re.compile(r"\$\{\{.*?\}\}")
PYTHON_HEREDOC = re.compile(r"\bpython(?:3)?\s+-\s+<<'(?P<marker>[A-Z_][A-Z0-9_]*)'\s*$")

FORBIDDEN_TOKENS = {
    "\u201c": "left smart double quote",
    "\u201d": "right smart double quote",
    "\u2018": "left smart single quote",
    "\u2019": "right smart single quote",
    "\uff08": "full-width left parenthesis",
    "\uff09": "full-width right parenthesis",
    "\u5982\u679c": "translated shell keyword: if",
    "\u7136\u540e": "translated shell keyword: then",
    "\u5426\u5219": "translated shell keyword: else",
    "\u7528\u4e8e": "translated shell keyword: for",
    "\u5b8c\u6210": "translated shell keyword: done",
    "\u5bfc\u5165": "translated Python keyword: import",
    "\u6765\u81ea": "translated Python keyword: from",
}


def workflow_files() -> list[Path]:
    return sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])


def script_blocks(path: Path, lines: list[str]) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = SCRIPT_START.match(lines[index])
        if not match:
            index += 1
            continue
        parent_indent = len(match.group("indent"))
        start_line = index + 2
        index += 1
        raw: list[str] = []
        while index < len(lines):
            line = lines[index]
            if line.strip() and len(line) - len(line.lstrip()) <= parent_indent:
                break
            raw.append(line)
            index += 1
        nonempty_indents = [len(line) - len(line.lstrip()) for line in raw if line.strip()]
        content_indent = min(nonempty_indents) if nonempty_indents else parent_indent + 2
        content = "\n".join(line[content_indent:] if line.strip() else "" for line in raw) + "\n"
        blocks.append((start_line, content))
    return blocks


def validate_forbidden_text(path: Path, text: str, errors: list[str]) -> None:
    for token, label in FORBIDDEN_TOKENS.items():
        if token not in text:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if token in line:
                errors.append(f"{path}:{line_number}: forbidden {label}")


def validate_ascii_script(path: Path, start_line: int, script: str, errors: list[str]) -> None:
    for offset, line in enumerate(script.splitlines()):
        characters = sorted({character for character in line if ord(character) > 127})
        if characters:
            codepoints = ", ".join(f"U+{ord(character):04X}" for character in characters)
            errors.append(f"{path}:{start_line + offset}: non-ASCII character in SSH script ({codepoints})")


def validate_python_heredocs(path: Path, start_line: int, script: str, errors: list[str]) -> None:
    lines = script.splitlines()
    index = 0
    while index < len(lines):
        match = PYTHON_HEREDOC.search(lines[index])
        if not match:
            index += 1
            continue
        marker = match.group("marker")
        heredoc_line = start_line + index
        index += 1
        body: list[str] = []
        while index < len(lines) and lines[index] != marker:
            body.append(lines[index])
            index += 1
        if index == len(lines):
            errors.append(f"{path}:{heredoc_line}: unterminated Python heredoc {marker}")
            continue
        try:
            compile("\n".join(body) + "\n", f"{path}:{heredoc_line}", "exec")
        except SyntaxError as exc:
            line_number = heredoc_line + (exc.lineno or 1)
            errors.append(f"{path}:{line_number}: invalid Python heredoc: {exc.msg}")
        index += 1


def find_bash() -> str | None:
    executable = shutil.which("bash")
    if executable:
        return executable
    windows_git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(windows_git_bash) if windows_git_bash.exists() else None


def validate_bash(path: Path, start_line: int, script: str, bash: str | None, errors: list[str]) -> None:
    if not bash:
        errors.append(f"{path}:{start_line}: bash executable is required for syntax validation")
        return
    normalized = GITHUB_EXPRESSION.sub("GITHUB_VALUE", script)
    with tempfile.NamedTemporaryFile("w", encoding="ascii", newline="\n", suffix=".sh", delete=False) as handle:
        handle.write(normalized)
        temporary_path = Path(handle.name)
    try:
        result = subprocess.run([bash, "-n", str(temporary_path)], capture_output=True, text=True, check=False)
        if result.returncode:
            message = (result.stderr or result.stdout).strip().replace(str(temporary_path), str(path))
            errors.append(f"{path}:{start_line}: invalid Bash script: {message}")
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    bash = find_bash()
    block_count = 0
    appleboy_count = 0

    for path in workflow_files():
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        validate_forbidden_text(path, text, errors)
        appleboy_count += text.count("appleboy/ssh-action@v1.0.3")
        for start_line, script in script_blocks(path, lines):
            block_count += 1
            validate_ascii_script(path, start_line, script, errors)
            validate_python_heredocs(path, start_line, script, errors)
            validate_bash(path, start_line, script, bash, errors)

    if appleboy_count and block_count < appleboy_count:
        errors.append(
            f"Expected at least {appleboy_count} script blocks for {appleboy_count} appleboy SSH actions; found {block_count}"
        )

    if errors:
        print("Workflow script validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Workflow script validation passed: {appleboy_count} SSH actions, {block_count} script blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
