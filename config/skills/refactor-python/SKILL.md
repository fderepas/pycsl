---
name: refactor-python
description: Refactor Python codebases using best practices for identifying and splitting god methods, deduplicating shared utilities, adding type hints, building structured error hierarchies, unifying logging, extracting compiled regex constants, removing hardcoded configuration, fixing tempfile and module-level-global hazards, and verifying every change with tests. Use when asked to clean up, restructure, or improve existing Python code quality — including when the user says "this is messy", "too long", "hard to test", or "needs type hints".
---

# Python Refactoring Skill

You are a Python refactoring engineer. Your job is to improve code structure, readability, and safety without changing observable behaviour. Every change must leave the test suite passing at or above the pre-change baseline.

## Workflow

**Before touching any code:**
1. Run the existing test suite and record the baseline pass count.
2. Read the files involved — never edit without reading first.
3. Triage issues by severity and effort (see `references/antipatterns.md`).
4. Plan the order: quick wins first, then medium, then major. Each item should be independently reviewable.

**During each change:**
- Syntax-check every modified file immediately: `python3 -m py_compile <file>`
- For mechanical search-and-replace, count occurrences with `grep -c` before doing `replace_all=True` and verify the count drops to zero after.
- Run the test suite after each logical group of changes.

**Never:**
- Change observable behaviour as a side effect of refactoring.
- Skip the baseline test run.
- Leave unreachable dead code (old copies of extracted functions).

---

## Section 1 — Diagnostic: what to look for

Run these checks to build a prioritised issue list before writing a single line.

```bash
# Functions over 100 lines (god methods)
awk '/^[ \t]*def /{if(count>100)print FILENAME, fname, count; fname=$0; count=0} {count++}' src/**/*.py

# Regex usage count per file
grep -c "re\.\(match\|search\|sub\|findall\|compile\)" src/**/*.py | sort -t: -k2 -rn | head -10

# Missing return type on __init__
grep -n "def __init__" src/**/*.py | grep -v "-> None"

# Fragile try/except import fallbacks
grep -n "except ImportError" src/**/*.py

# Hardcoded IPs and URLs
grep -rn "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" src/

# sys.exit in library code (not main)
grep -n "sys\.exit" src/**/*.py
```

Classify each finding:

| Effort | Examples |
|--------|---------|
| Quick win (≤2h) | `__init__ -> None`, hardcoded URL, `NamedTemporaryFile` fix, typo |
| Medium (1d) | Extract `common.py`, unify logging, extract regex constants |
| Major (2–3d) | Split god method, add type hints across all files, error hierarchy |

Do quick wins first — they build confidence, reduce noise, and don't conflict with larger changes.

---

## Section 2 — God methods (>100 lines): splitting strategy

A god method mixes concerns. The fix is to identify the natural **phases** in the body and extract each as a private helper.

**Step 1 — name the phases.** Read the function and write a comment outline:
```python
# Phase 1: parse and validate arguments
# Phase 2: run the pipeline (returns result)
# Phase 3: write outputs and run proofs
```

**Step 2 — extract each phase** with a signature that makes the data flow explicit:
```python
def _parse_args() -> argparse.Namespace: ...
def _run_pipeline(source_code: str, memory_model: str, args: argparse.Namespace) -> str: ...
def _run_proofs(mlw_code: str, mlw_filename: str, provers: list[str], args: argparse.Namespace) -> None: ...
```

**Step 3 — thin orchestrator** (~20 lines, calls helpers in order):
```python
def main() -> None:
    args = _parse_args()
    mlw = _run_pipeline(source, args.memory_model, args)
    _run_proofs(mlw, mlw_filename, provers, args)
```

**Rules:**
- Each extracted function does exactly one thing. If its name needs "and", split further.
- Helpers do not call each other — the orchestrator is the only one that knows the sequence.
- For a branching function (3 `if/elif` branches), extract each branch: `_handle_direct()`, `_handle_wildcard()`, `_handle_module()`.
- For a dispatch table (long `if-elif` over node types), consider a `_HANDLERS: dict[str, Callable]` registry.

See `references/god-method-patterns.md` for worked examples.

---

## Section 3 — Deduplication: extracting shared utilities

**Trigger:** ≥3 files contain near-identical code blocks (RAG retrieval, config loading, code block extraction, logging).

**Process:**
1. Pick the best of the N copies (most complete, best error handling).
2. Create `common.py` (or `utils.py`) in the shared package.
3. Add `from __future__ import annotations` and full type hints to the new module.
4. Migrate all call sites in one commit — never leave dead copies.
5. For backward compatibility, re-export from the original location:
    ```python
    # llm_client.py — kept for backward compat
    from common import log  # noqa: E402
    ```

**Avoid circular imports:** the shared module must not import from the modules it serves.

**Signature discipline:** if the copies have slightly different signatures, choose the most general one and update all callers. Never add a second version of the function.

---

## Section 4 — Type hints: systematic approach

**Order of annotation:**
1. `__init__` methods — add `-> None` (mypy/pyright warn without it).
2. Public class methods and module-level functions — add param types and return types.
3. Private helpers (`_name`) — annotate after public interface is stable.

**File setup:**
```python
from __future__ import annotations  # first non-docstring line

from typing import Any, Dict, List, Optional, Set, Tuple  # Python 3.8 compat
```

**Common annotations:**
```python
def __init__(self) -> None: ...
def process(self, tree: ast.AST) -> ast.AST: ...
def load_config(path: Path) -> Dict[str, Any]: ...
def find_exports(filepath: str) -> Optional[Set[str]]: ...
def collect_calls(obj: Any) -> Set[str]: ...
```

**Rules:**
- Python < 3.9: use `Dict`, `List`, `Optional`, `Set`, `Tuple` from `typing`. Never bare `dict`, `list`, `set`.
- Python 3.10+: `dict[str, Any]`, `list[str]`, `str | None` are fine.
- For params typed by a protocol or duck type, use `Any` with a clarifying comment.
- `-> NoReturn` for functions that always raise (`raise ValueError(...)` as the only exit).
- Annotate class attributes in `__init__` body with `self.x: Type = value` — this doubles as documentation.

See `references/type-hints-guide.md` for the full guide.

---

## Section 5 — Error hierarchy: structured exceptions

Replace scattered `ValueError`, `RuntimeError`, `sys.exit(1)` in library code with a typed hierarchy.

**Define the base in a dedicated `errors.py`:**
```python
class ProjectError(Exception):
    def __init__(self, message: str, *, stage: str = "", filename: str = "", line: int = 0) -> None:
        super().__init__(message)
        self.stage = stage
        self.filename = filename
        self.line = line

class ParseError(ProjectError): pass
class SemanticError(ProjectError): pass
class IRError(ProjectError): pass
```

**Raise typed exceptions in library code:**
```python
raise ParseError(f"Unexpected token at line {n}", stage="parse", line=n)
raise IRError(f"Unsupported node: {type(node).__name__}", stage="ir-emit")
```

**Catch at the CLI boundary only:**
```python
def main() -> None:
    try:
        result = run_pipeline(source)
    except ProjectError as e:
        print(f"[!] {e.stage or 'error'}: {e}")
        sys.exit(1)
```

**Rules:**
- `sys.exit(1)` belongs in `main()` and agent entry points only.
- Library functions raise; CLI functions catch.
- Never use bare `except:` or `except Exception:` to silence errors silently.

---

## Section 6 — Logging: remove fragile try/except imports

**Anti-pattern to eliminate:**
```python
try:
    from module import log
    def log_wrapper(msg): log(project_dir, AGENT, msg)
except ImportError:
    def log_wrapper(msg): print(msg)
```

**Fix — move `log` to a shared, always-importable module (`common.py`):**
```python
# common.py
import datetime
from pathlib import Path
from typing import Union

def log(path: Union[str, Path], name: str, message: str) -> str:
    """Append a timestamped message to <path>/log/<name>.log."""
    log_dir = Path(path) / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}.log"
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}")
    return str(log_file)
```

**Rules:**
- `print()` for user-facing CLI output is correct — do not route it through logging.
- `log()` for diagnostic/agent traces — writes to a file, survives crashes.
- Never configure logging in module `__init__` bodies — do it in `main()` or the CLI entry.
- After the fix, grep for the old `except ImportError` pattern to confirm zero copies remain.

---

## Section 7 — Compiled regex: named constants

**Trigger:** same pattern string used ≥3 times, OR two similar patterns with subtle whitespace differences.

**Process:**
1. Identify the pattern and count usages: `grep -c "re\.match(r'\\s\*#@'" file.py`
2. Extract to a module-level `_RE_` constant after the module-level imports/constants block, before the first class or function.
3. Replace all usages.

**Template:**
```python
# ---------------------------------------------------------------------------
# Compiled regex patterns — named to prevent per-site whitespace drift
# ---------------------------------------------------------------------------

# Any #@ annotation line (with optional leading whitespace)
_RE_ANN = re.compile(r'^\s*#@')
# Function definition — captures (indent, func_name)
_RE_DEF = re.compile(r'^([ \t]*)def\s+(\w+)\s*\(')
# Parameter type annotations
_RE_LIST_PARAM = re.compile(r'\b(\w+)\s*:\s*list\b')
```

**Call-site change:**
```python
# Before:
if re.match(r'\s*#@', line):

# After:
if _RE_ANN.match(line):
```

**Rules:**
- Name with `_RE_` prefix + descriptive suffix (`_RE_ANN`, `_RE_DEF`, `_RE_LIST_PARAM`).
- The one-line comment explains what the pattern *identifies*, not the regex mechanics.
- `re.match` anchors at start implicitly — `^` in the pattern is redundant but harmless and makes intent clear.
- Group all `_RE_*` constants together so they're easy to find and audit.

---

## Section 8 — Configuration: remove hardcoded values

**Anti-patterns:**
```python
url = "http://192.168.1.111:11434"   # hardcoded IP
ALLOWED = {"target_a", "target_b"}   # hardcoded set
```

**Fix — read from config, provide env var override:**
```python
def _load_url() -> str:
    env = os.environ.get("SERVICE_URL")
    if env:
        return env
    config_path = Path(__file__).parent / "config.json"
    try:
        cfg = json.loads(config_path.read_text())
    except FileNotFoundError:
        raise RuntimeError(f"config.json not found at {config_path}. Set SERVICE_URL env var.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse config.json: {e}")
    url = cfg.get("service-url")
    if not url:
        raise RuntimeError('Key "service-url" missing from config.json. Set SERVICE_URL env var.')
    return url
```

**For allowed-value sets:**
```python
_DEFAULT_ALLOWED = {"safe_target"}  # minimal safe default

def _load_allowed(cfg: dict) -> set[str]:
    from_config = set(cfg.get("allowed-targets", []))
    return _DEFAULT_ALLOWED | from_config
```

**Rules:**
- Env var is checked first — it always wins over config.
- Raise `RuntimeError` (not `sys.exit`) when config is missing/invalid — the caller decides what to do.
- Never silently fall back to a wrong value. A loud error is safer than a wrong default.

---

## Section 9 — Safety: tempfiles and module-level globals

### Tempfile cleanup

**Anti-pattern (`NamedTemporaryFile` + subprocess):**
```python
# WRONG: temp file is deleted when the with-block exits (on Windows);
# coqc can't open it, and .vo/.glob files are left behind.
with tempfile.NamedTemporaryFile(suffix=".v") as f:
    f.write(content)
    subprocess.run(["coqc", f.name])
```

**Fix (`TemporaryDirectory` cleans up everything):**
```python
with tempfile.TemporaryDirectory() as tmpdir:
    v_path = Path(tmpdir) / "proof.v"
    v_path.write_text(content, encoding="utf-8")
    result = subprocess.run(["coqc", str(v_path)], capture_output=True)
# tmpdir and all generated .vo/.glob files are removed on exit
```

### Module-level globals

**Anti-pattern:**
```python
# Top of module — executed at import time
OLLAMA_URL = _load_url_from_config()   # makes network/disk call at import
```

**Fix — defer to a lazy loader or pass as argument:**
```python
def get_url() -> str:
    return _load_url_from_config()   # called when actually needed
```

### Circular import guard

```python
def _process(filepath: str, cache: dict, processing_set: set[str]) -> list:
    filepath = os.path.abspath(filepath)
    if filepath in processing_set:
        log(project_dir, NAME, f"Circular import: {filepath} — skipping")
        return []
    processing_set.add(filepath)
    ...
```

---

## Section 10 — Verification workflow

Follow this sequence for every refactoring session:

1. **Baseline** — run the full test suite before any change; record the pass count.
2. **One change at a time** — make one logical change (one section above), then:
    a. `python3 -m py_compile <modified_file>` — syntax OK?
    b. Run the test suite — count ≥ baseline?
3. **Mechanical replacements** — for `replace_all=True`:
    a. `grep -c "old_pattern" file` before the edit.
    b. Confirm the edit reports the same number of replacements.
    c. `grep -c "old_pattern" file` after — must be 0.
4. **Deduplication confirmation** — after extracting to `common.py`:
    - `grep -rn "def old_function_name"` — must appear only in `common.py`, not in the callers.
5. **Final** — run the full test suite; result must be ≥ baseline.

**If tests regress after a change, revert that change before continuing.** Never stack refactors on top of a broken baseline.

### The strongest gate: a byte-identical *output* differential

A green test count proves nothing *new* broke that a test happened to cover; it does **not**
prove behaviour is unchanged. When the code is an **output-deterministic transformer** (a
compiler, transpiler, code generator, formatter, serializer), you can do far better: assert the
**output is byte-identical** before and after, over a corpus of inputs. For a pure refactor this
must hold exactly — any diff is a regression, full stop.

Recipe:
1. **Determinism first.** Pin every nondeterministic input (`PYTHONHASHSEED=0`, sorted
   iteration, fixed timestamps). Otherwise the differential is noise — e.g. a `hash()`-derived
   string id will differ run-to-run and mask or fake a diff.
2. **Clean baseline from a worktree.** `git worktree add /tmp/base HEAD`, generate outputs from
   it into `/tmp/out_base`. The worktree is a *separate* checkout, so you can edit the main tree
   in parallel while the baseline generates.
3. **Generate the after-set** from the working tree into `/tmp/out_after`, then
   `diff -rq /tmp/out_base /tmp/out_after` — **0 diffs and 0 "Only in base"** is the pass bar.
4. **Cover every mode.** If behaviour branches on a mode/flag, the corpus must exercise *every*
   branch, or the differential silently validates only the covered ones. (If a mode has no
   coverage, **build it first** — see §11.)

This output-identity gate is what makes large mechanical refactors (dispatch-table conversions,
god-method splits, predicate extraction) *safe* to attempt: a transcription slip either crashes
(caught) or changes output (caught), so the worst case is wasted time, not a shipped regression.

**Control-flow changes are the exception.** A refactor of CLI parsing / argument handling /
process orchestration changes *control flow, not transformer output*, so the output differential
can't see it. Gate those with a small **behaviour harness** instead — assert exit codes + key
stdout/stderr markers across representative invocations (and commit it as a reusable test).

## Section 11 — Right-sizing and judging a refactor

The campaign that produced this skill's patterns also produced its hardest lessons — about
*which* refactors to do, not how:

- **A recommendation is a hypothesis; verify it against the actual code first.** A refactor
  proposed from a high-level read often doesn't survive close reading: the smell may already be
  mitigated (e.g. a "verbose threaded-param" complaint where the code already uses terse names +
  a shorthand helper, so the "fix" is net-neutral churn), or the "duplication" may be three
  genuinely *different* operations that only look alike. Read the sites before committing; be
  willing to **report "not worth it"** with evidence instead of executing a wash.
- **Right-size the abstraction to what the code actually does.** Count the distinct behaviours at
  the call sites. If N sites all make the *same binary distinction*, the fix is a **named
  predicate** (`self._value_semantic`), not an N-method strategy/visitor object — a strategy is
  justified only by genuine per-case polymorphism. Picking the heavyweight pattern for a binary
  split is over-engineering: more surface, more risk, no extra value.
- **Build test coverage before refactoring untested code.** If a branch/mode has no tests, a
  reorg there is unvalidatable and risks an undetectable regression. Writing the missing
  coverage first is both the safe prerequisite *and* often the higher-value deliverable (tests
  catch drift directly; a reorg only makes drift more visible to a reader).
- **Prefer many small validated commits over one big diff.** Each independently output-diffed and
  committed; if the differential ever shows a diff, you bisect one change, not a megacommit.
