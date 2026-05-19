---
name: refactor-python-antipatterns
description: Catalogue of detectable Python anti-patterns with severity rating, effort estimate, and grep command to find each one. Use when triaging a codebase before starting a refactoring session.
---

# Python Anti-Pattern Catalogue

Use these checks during the diagnostic phase (Section 1 of the main skill). Run them on the target codebase, then sort findings by severity and group by effort to build a prioritised work plan.

---

## High severity

### H1 — God method (function > 100 lines)

**Why it matters:** Untestable in isolation, impossible to understand in one read, resists change.

**Detection:**
```bash
# Print filename, function name, and line count for functions over 100 lines
python3 - <<'EOF'
import ast, sys
from pathlib import Path

for path in Path("src").rglob("*.py"):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = max(getattr(n, "end_lineno", node.lineno) for n in ast.walk(node))
            size = end - node.lineno
            if size > 100:
                print(f"{path}:{node.lineno}  {node.name}  ({size} lines)")
EOF
```

**Fix:** See Section 2 (God methods) in the main skill.

---

### H2 — Duplicated utility in ≥3 files

**Why it matters:** Fixes applied to one copy silently miss the others; behaviour diverges over time.

**Detection:**
```bash
# Find near-identical function names across files
grep -rn "def retrieve_skill_chunks\|def extract_code_block\|def load_config" src/
```

**Fix:** Extract to `common.py`; re-export from original location for backward compat. See Section 3.

---

### H3 — Fragile try/except ImportError fallback

**Why it matters:** Silent fallback to a `print`-based stub means errors in agent logs are silently dropped when the module is run standalone.

**Detection:**
```bash
grep -n "except ImportError" src/**/*.py
```

**Pattern to find:**
```python
try:
    from module import log
except ImportError:
    def log(*args): print(*args)
```

**Fix:** Move `log` (or the shared utility) to a module that is always on `sys.path`. See Section 6.

---

### H4 — Hardcoded IP address or URL in Python source

**Why it matters:** The URL changes; every deploy that differs from the hardcoded value silently uses the wrong endpoint.

**Detection:**
```bash
grep -rn "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" src/
grep -rn "http://\|https://" src/ | grep -v "#"
```

**Fix:** Read from config file + env var override; raise `RuntimeError` if absent. See Section 8.

---

### H5 — `NamedTemporaryFile` used with a subprocess

**Why it matters:** On Windows the file is deleted when the `with` block exits, before the subprocess can open it. On Unix, auxiliary files (`.vo`, `.glob`, `.pyc`) are left behind on crash.

**Detection:**
```bash
grep -n "NamedTemporaryFile" src/**/*.py
```

**Fix:** Replace with `tempfile.TemporaryDirectory()`. See Section 9.

---

## Medium severity

### M1 — `__init__` missing `-> None`

**Why it matters:** mypy and pyright warn; absence signals that no one has type-checked this file.

**Detection:**
```bash
grep -n "def __init__" src/**/*.py | grep -v "-> None"
```

**Fix:** Mechanical — add `-> None` to every `def __init__(self...):`. See Section 4.

---

### M2 — Inline regex pattern used ≥3 times

**Why it matters:** Patterns drift apart silently (e.g., `\s*#@` vs `[ \t]*#@` vs `#@`). Bugs introduced in one copy don't propagate to others.

**Detection:**
```bash
# Count raw string occurrences for the most common patterns
grep -o "r'[^']*'" src/path/to/file.py | sort | uniq -c | sort -rn | head -20
```

**Fix:** Extract to `_RE_NAME = re.compile(r'...')` at module level. See Section 7.

---

### M3 — Missing type hints on public API

**Why it matters:** IDE completion absent, interface contracts invisible, refactoring riskier.

**Detection:**
```bash
# Count def lines vs lines with ->
echo "Total defs: $(grep -c '^def \|^    def ' src/file.py)"
echo "With return type: $(grep -c '\->' src/file.py)"
```

**Fix:** See Section 4 and `references/type-hints-guide.md`.

---

### M4 — `print()` for diagnostic/agent output

**Why it matters:** print output is lost when stdout is piped; it conflates user-facing messages with debug traces; no timestamps.

**Detection:**
```bash
grep -n "^[ \t]*print(" src/agents/*.py
```

**Note:** `print()` is correct for user-facing CLI output (e.g., `[*] Processing file.py`). The issue is using `print` in agent/library code instead of `log()`.

**Fix:** Replace with `log(project_dir, AGENT_NAME, msg)` in agent/library code. See Section 6.

---

### M5 — Module-level code with side effects

**Why it matters:** Any import of the module triggers the side effect (network call, file read, subprocess). Makes testing impossible, slows startup, and fails in environments where the resource is unavailable.

**Detection:**
```bash
# Look for top-level function calls outside class/def
python3 - <<'EOF'
import ast
from pathlib import Path

for path in Path("src").rglob("*.py"):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            print(f"{path}:{node.lineno}  top-level call: {ast.dump(node.value.func)[:60]}")
EOF
```

**Fix:** Wrap in a function called lazily or passed as an argument. See Section 9.

---

### M6 — `sys.exit(1)` inside library/agent code

**Why it matters:** Prevents the caller from handling the error; makes the module untestable.

**Detection:**
```bash
grep -n "sys\.exit" src/**/*.py | grep -v "main()\|__main__"
```

**Fix:** Raise a typed exception; let `main()` or the CLI entry point call `sys.exit`. See Section 5.

---

## Low severity

### L1 — Typo in variable/function name

**Detection:** `grep -rn "skill_anotator\|recieve\|seperate"` — add domain-specific typos as you find them.

**Fix:** `replace_all=True` rename — check all usages before and after.

---

### L2 — Hardcoded version string

**Detection:**
```bash
grep -rn '"[0-9]\+\.[0-9]\+\.[0-9]\+"' src/
```

**Fix:** Move to config file or derive from the installed package at runtime.

---

### L3 — `except (FileNotFoundError, json.JSONDecodeError)` silenced without logging

**Why it matters:** Errors disappear silently; debugging production issues becomes guesswork.

**Detection:**
```bash
grep -A2 "except" src/**/*.py | grep -B1 "pass\|return None\|return {}\|return \[\]"
```

**Fix:** Log the exception before returning a default, or re-raise as a typed `ProjectError`.
