"""Developer Assistant Tools (Code Inspection, Syntax Checking, Git Advice)."""

import py_compile
import subprocess
from pathlib import Path
from config.settings import BASE_DIR


def inspect_code(filepath: str, start_line: int = 1, max_lines: int = 60) -> str:
    """Inspect local code file content with line numbers for debugging or code review."""
    try:
        p = Path(filepath)
        if not p.is_absolute():
            p = BASE_DIR / p

        if not p.exists():
            return f"File '{filepath}' not found."
        if p.is_dir():
            return f"'{filepath}' is a directory."

        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), start_idx + max_lines)
        selected = lines[start_idx:end_idx]

        out = [f"File: {filepath} (Lines {start_idx + 1} to {end_idx} of {len(lines)}):"]
        for idx, line in enumerate(selected, start=start_idx + 1):
            out.append(f"{idx:4d} | {line.rstrip()}")
        return "\n".join(out)
    except Exception as e:
        return f"Error reading code file: {e}"


def check_python_syntax(filepath: str) -> str:
    """Validate python file syntax using py_compile to catch SyntaxError or IndentationError."""
    try:
        p = Path(filepath)
        if not p.is_absolute():
            p = BASE_DIR / p

        if not p.exists():
            return f"File '{filepath}' does not exist."

        py_compile.compile(str(p), doraise=True)
        return f"Syntax check PASSED: '{filepath}' contains valid Python code."
    except py_compile.PyCompileError as e:
        return f"Syntax check FAILED for '{filepath}':\n{e}"
    except Exception as e:
        return f"Error compiling file '{filepath}': {e}"


def git_helper(query: str) -> str:
    """Get accurate git commands for common version control operations."""
    q = query.lower()
    recipes = {
        "undo commit": "git reset --soft HEAD~1   # Undoes last commit, keeps changes staged\ngit reset HEAD~1          # Undoes last commit, keeps changes unstaged",
        "discard changes": "git restore <file>        # Discard unstaged changes to a file\ngit restore .             # Discard all unstaged changes",
        "stash": "git stash push -m 'wip'  # Stash current uncommitted changes\ngit stash list             # View stashes\ngit stash pop              # Restore stashed changes",
        "status": "git status -s             # Compact status of changed files",
        "diff": "git diff                  # View unstaged diff\ngit diff --staged         # View staged diff",
        "branch": "git checkout -b <name>    # Create and switch to new branch\ngit branch -a             # List all branches",
        "log": "git log --oneline -n 10   # View recent 10 commits concisely",
    }

    for key, val in recipes.items():
        if key in q:
            return f"Git command for '{key}':\n```bash\n{val}\n```"

    return (
        "Common Git Recipes:\n"
        "• Undo commit: `git reset --soft HEAD~1`\n"
        "• Stash work: `git stash && git stash pop`\n"
        "• Discard changes: `git restore <file>`\n"
        "• View log: `git log --oneline -n 10`"
    )


def run_command_safe(command: str) -> str:
    """Safely run read-only or developer diagnostic commands (e.g. 'git status', 'python3 -V')."""
    cmd = command.strip()
    # Security filter: restrict destructive commands
    blocked = ["rm -rf", "mkfs", "dd ", "shutdown", "reboot", ":(){ :|:& };:"]
    if any(b in cmd for b in blocked):
        return f"Command execution rejected for safety: dangerous pattern in '{cmd}'."

    try:
        res = subprocess.run(
            cmd,
            shell=True,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
        )
        out = res.stdout.strip()
        err = res.stderr.strip()
        result = out if out else err
        return result if result else f"Command completed with return code {res.returncode}."
    except Exception as e:
        return f"Execution error: {e}"
