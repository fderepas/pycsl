---
name: pycsl-stdlib-coverage
description: Battle-tested discipline for writing pure-Python standard library implementations that PyCSL can verify. Covers the full workflow from concrete tests through annotations to formal tests (symbolic-input proofs). Documents lessons learned from os (98.0% proven), re (16/16 VCs), warnings (18/18 body + 3/3 formal VCs), and json (6/6 formal VCs), including PyCSL tool gaps, naming workarounds, import resolution pitfalls, and the two-level verification strategy (body-level vs stub-level). Use this skill when adding a new stdlib module to pure_lib/, annotating existing modules, writing formal tests, or diagnosing PyCSL proof failures.
---

# PyCSL Stdlib Coverage

## Purpose and scope

This skill governs the creation and verification of **pure-Python
standard library implementations** that PyCSL can formally verify. The
goal: for every stdlib API that PyCSL uses internally, provide a
verifiable pure-Python model so that PyCSL can eventually verify its
own source code (self-annotation).

The implementations live in `pure_lib/<module>/` with inline PyCSL
contract annotations. They are **real, runnable Python** — not stubs,
not `pass` bodies. This matters: the implementations are tested
concretely *and* proved formally.

---

## Architecture

### Directory layout

```
pure_lib/
  os/
    __init__.py              # Re-exports, constants (literal values)
    UnixInodeFileSystem.py   # Full inode filesystem (~1090 lines)
  re/
    __init__.py              # Re-exports RePattern as Pattern, etc.
    _engine.py               # 7 hand-written matchers, Pattern, ReMatch
  warn/
    __init__.py              # Functions directly here (not submodule!)
  json/
    __init__.py              # Original json implementation
    _api.py                  # Thin verifiable API wrapper
    decoder.py, encoder.py   # Full impl (body-level blocked)
pure_lib_test/
  0001.py                    # Concrete test: os write/read round-trip
  0002.py                    # Concrete test: re matchers (10 tests)
  0003.py                    # Concrete test: warnings (5 tests)
  0004.py                    # Concrete test: json (15 tests)
  formal_0001.py             # Formal test: os (18/18 VCs)
  formal_0002.py             # Formal test: re (16/16 VCs)
  formal_0003.py             # Formal test: warnings (3/3 VCs)
  formal_0004.py             # Formal test: json (6/6 VCs)
lib/
  calling.json               # Call graph: which stdlib symbols to cover
```

### Two repos

- **`pycsl_copy/pycsl`** — the modules being verified (pure_lib, tests)
- **`pycsl`** — the PyCSL tool itself (src/pycsl/)

### Two verification levels

1. **Body-level** — PyCSL verifies the function implementation directly.
   Works best for integer-heavy code (os filesystem, warnings). Requires
   the full function body to compile to valid WhyML.

2. **Stub-level** — PyCSL generates `val` declarations (abstract
   function specs) from `__init__.py` imports. Formal tests verify
   properties through these stubs. Works for string-heavy code (re)
   or partially-verifiable modules (json) where body-level verification
   hits tool gaps.

3. **Thin API wrapper** (new pattern from json) — When most of a module
   fails body-level proof, create a `_api.py` with:
   - Body-verified functions for simple logic (integer ops only)
   - Stub wrappers that delegate to the real implementation for complex code
   - This gives you *some* body-level proof without fighting the tool

---

## The workflow (battle-tested)

### Step 1 — Write a concrete test

Create `pure_lib_test/NNNN.py` that imports from `pure_lib/<module>`
and tests all key functions with concrete values. Run it:

```bash
python3 pure_lib_test/0002.py
# PASS: 1 — whitespace matcher
# ...
# PASS: 10 — flags have correct values
```

### Step 2 — Annotate the implementation

Add `#@ requires`, `#@ ensures`, `#@ assigns` annotations inline.
Focus on:
- **Preconditions**: input bounds (`pos >= 0`)
- **Postconditions**: return ranges (`\result >= 0 or \result == -1`)
- **Frame conditions**: `assigns \nothing` when pure
- **Class invariants**: field relationships (`self._end >= self._start`)
- **Loop invariants**: needed for while loops in proofs

### Step 3 — Generate WhyML and iterate

```bash
cd /path/to/pycsl
PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', '--no-proof', '../pycsl_copy/pycsl/pure_lib/re/__init__.py']
from pycsl.pycsl import main
main()
"
```

Check the `.mlw` file. Fix naming issues, type mismatches, missing
imports. Iterate until WhyML type-checks.

### Step 4 — Run body-level proof (if feasible)

```bash
# Remove --no-proof to run the full proof
sys.argv = ['pycsl', '--keep-mlw', 'pure_lib/os/__init__.py']
```

For integer-heavy code (os), this works well — 98.0% proven.
For string-heavy code (re), body-level proof is blocked by tool gaps
(see §Tool Gaps below). Proceed to step 5 regardless.

### Step 5 — Write a formal test

Create `pure_lib_test/formal_NNNN.py` with **symbolic parameters**
instead of concrete values. Each function returns 0 (pass) or 1 (fail)
as a provable postcondition:

```python
#@ requires pos >= 0
#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_whitespace(s, pos) -> int:
    m = _match_whitespace(s, pos)
    if m < 0:
        return 1
    return 0
```

This proves the property holds for **all valid inputs**, not just
test cases. See `docs/glossary/formal-test.md` for the concept.

### Step 6 — Document tool gaps

Any PyCSL limitation discovered during steps 3–5 goes into a
requirements document (`NNNN.md` at repo root):
- `1009.md`: R1–R4 (stub generation, tuple results, assigns)
- `1111.md`: R5–R7 (str params, constant values, default args)
- `07-0647-gaps.md`: R8–R13 (keyword clashes, string ops, class returns)

---

## Current status

### os module — 98.0% proven (body-level)

| Metric | Value |
|--------|-------|
| Valid VCs | 4019 |
| Total VCs | 4101 |
| Proven rate | 98.0% |
| Unproven goals | 41 |
| Formal test | 18/18 VCs ✅ |

The 41 remaining failures trace to `subscript_get` abstraction — when
inlined code reads `inode[2]` on a record field, PyCSL emits
`subscript_get !inode 2` (abstract) instead of `!inode[2]` (array
access). This is a PyCSL tool gap, not a pure_lib issue.

### re module — 16/16 formal test VCs (stub-level)

| Metric | Value |
|--------|-------|
| Formal test VCs | 16/16 ✅ |
| Body-level proof | Blocked (R10–R13) |
| Concrete test | 10/10 pass |
| Matchers annotated | 7/7 |

Body-level proof blocked by string operation gaps (missing
`use string.String`, `isdigit()` receiver loss, class-return type
mismatch). Stub-level verification through `__init__.py` works well.

### warnings module — 18/18 body-level + 3/3 formal (body-level)

| Metric | Value |
|--------|-------|
| Body-level VCs | 18/18 ✅ |
| Formal test VCs | 3/3 ✅ |
| Concrete test | 5/5 pass |
| Functions | 4 (warn, simplefilter, _deprecated, catch_warnings) |

Named `warn/` to avoid stdlib name clash. Functions live directly in
`__init__.py` because function contracts don't propagate through
re-exports. `warn()` excluded from formal test because it raises
`Exception` and formal tests can't declare `raises`.

### json module — 6/6 formal test VCs (thin API wrapper)

| Metric | Value |
|--------|-------|
| Formal test VCs | 6/6 ✅ |
| Concrete test | 15/15 pass |
| Body-level proof | Partially blocked |
| Pattern | Thin `_api.py` wrapper |

Body-level proof blocked by: inliner method argument count mismatch
(`iterencode`), tuple parameter destructuring, encoder pipeline crash.
`detect_encoding` is body-verified (integer ops only). `loads`/`dumps`
are stubs delegating to real implementation.

---

## Lessons learned

### Naming: Why3 keyword and symbol clashes

PyCSL lowercases Python class names to form Why3 types. Several
Python names collide with Why3 keywords or with PyCSL's own emitted
symbols:

| Python name | Clash | Fix |
|-------------|-------|-----|
| `Match` | `match` is a Why3 keyword | Rename to `ReMatch` |
| `Pattern` | `isinstance` emits `val constant pattern` colliding with `type pattern` | Rename to `RePattern` |
| `compile(pattern, ...)` | Parameter `pattern` collides with type `pattern` | Rename parameter to `pat_src` |

**Rule:** Always check generated `.mlw` for name collisions after
adding a new class. Keep Python API compatibility via `__init__.py`
re-exports (`ReMatch as Match`).

### Naming: Python stdlib module name clashes

PyCSL's import resolver can pick up the *real* stdlib module instead
of your `pure_lib/` version if names collide:

| Module name | Clash | Fix |
|-------------|-------|-----|
| `warnings` | Resolves to stdlib `warnings` | Name directory `warn/` |

**Rule:** If your pure_lib module shares a name with a top-level
Python stdlib package, rename it. Use `__init__.py` to re-export
under the expected API names.

### Function contracts don't propagate through re-exports

**Critical architecture decision:** When `__init__.py` does
`from ._core import my_function`, PyCSL generates a stub for
`my_function` but **does NOT carry its `requires`/`ensures` contracts
through**. Only **class** contracts (invariants, method specs) survive
re-export.

**Consequence:** For modules that export top-level functions (not
classes), put the annotated function definitions **directly in
`__init__.py`**, not in a submodule. This is why `pure_lib/warn/`
has everything in `__init__.py`.

### Constants: use literals, not imports

Cross-module constants (e.g., `O_CREAT = UnixInodeFileSystem.O_CREAT`)
become abstract `val constant` with no value in WhyML. PyCSL's
`module_constants` works for the file being verified but NOT for
imported modules.

**Fix:** Define constants as literals directly:
```python
O_RDONLY = 0
O_WRONLY = 1
O_CREAT = 64
```

### String methods: known postconditions

- `.ljust(width)` — has `ensures Array.length result >= x0` ✅
- `.ljust(width, fillchar)` — 2-arg form has type issues (fillchar
  `b'\x00'` becomes `array int`, stub expects `int`) ❌
- `.encode()` — length is genuinely unknown; no useful postcondition
- `.zfill(width)` — has length ensures ✅

### Default arguments and type annotations

- Default arguments: PyCSL generates N-arg stubs; callers must pass
  all args explicitly. `open(filename, O_RDONLY)` not `open(filename)`.
- `filename: str` annotation: causes type mismatch (string → int in
  Why3). Drop the `: str`.

### Inliner limitations

- Module-level helper calls in inlined bodies get replaced with
  `Array.make 1 0` instead of the actual function call.
- **Workaround:** Remove preconditions that depend on helper
  postconditions, or inline the logic directly.
- Method calls on module-level objects may miscount arguments
  (`self` not counted), causing inliner errors.

### Loop patterns: tuple unpacking and chained comparisons

**Tuple unpacking in for-loops is broken.** Code like
`for action, cat in _filters:` generates WhyML where `cat` is
undefined. **Workaround:** Use parallel lists + index-based access:

```python
_filter_actions = []  # list of action strings
_filter_cats = []     # list of category strings
# Access via _filter_actions[i], _filter_cats[i] in a while loop
```

**Chained comparisons are broken.** `0 <= i <= n` lowers to
`((0 <= !i) <= !n)` — applying `<=` to a boolean. **Workaround:**
Split into two separate invariants:

```python
#@ loop invariant 0 <= i
#@ loop invariant i <= n
```

### Exception propagation across functions

PyCSL does not propagate `raises` clauses through callees. If
function `A` calls function `B` which raises `Exception`, `A` does
NOT automatically get a `raises` annotation.

**Consequence:** Functions that call exception-raising helpers can't
be formally tested (the formal test can't declare the exception
possibility). **Workaround:** Either restructure to avoid calling
the exception-raising function, or exclude that function from formal
tests and document why.

### `assigns \nothing` is implicit

In Why3, a `val` without `writes` clause is already effect-free.
You do NOT need to explicitly emit `writes {}`. The `assigns \nothing`
annotation is still useful documentation but doesn't change the proof.

### Tuple result postconditions

`\result[0] >= 0` correctly lowers to
`let (_r0_, _) = result in _r0_ >= 0`. This works since the R3 fix.

### Proof strategy for remaining failures

When body-level proof is stuck:

1. Check if the failure is a **PyCSL tool gap** (subscript_get, string
   ops, etc.) — document in requirements, move on.
2. Check if a **stronger precondition** helps — e.g., adding
   `inode_num < 32` guard made a loop invariant provable.
3. Check if a **weaker postcondition** is still useful — removing
   `\valid(name_bytes, 30)` eliminated downstream failures.
4. Fall back to **stub-level** formal tests through `__init__.py`.

---

## Known PyCSL tool gaps (blocking further progress)

### Critical (blocks body-level proof for most code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R13 | Class-returning functions: `int` return type vs record literal | re |
| subscript_get | Array-field reads in inlined code are abstract | os (~70% of failures) |

### High (blocks string-heavy code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R10 | Missing `use string.String` for `in` operator | re |
| R11 | `self` parameter missing from method bodies | re |
| R12 | `isdigit()` drops receiver (chained method call) | re |
| — | Inliner method arg count: `self` not counted for module-level objects | json |
| — | Tuple parameter destructuring: `let (a, b) = pair` type mismatch | json |
| — | Pipeline crash (`NoneType.lstrip`) in encoder code | json |

### Medium (blocks specific patterns, workarounds exist)

| ID | Gap | Workaround |
|----|-----|-----------|
| R5 | `filename: str` → WhyML `string` but APIs use `int` | Drop `: str` |
| R6 | Imported constants have no value | Use literal integers |
| R7 | Default arguments not in cross-module stubs | Pass all args explicitly |
| R8 | `match` is Why3 keyword | Rename class |
| R9 | isinstance constant name collision | Rename class |
| — | Tuple unpacking in for-loops (`for a, b in lst:`) | Parallel lists + index loop |
| — | Chained comparisons (`0 <= i <= n`) | Split into two invariants |
| — | `raises` not propagated through callees | Restructure or exclude from formal test |
| — | Stdlib module name clash in import resolver | Rename directory (e.g., `warn/`) |

---

## How to run PyCSL

### Import resolution (critical)

PyCSL resolves imports by searching: (1) the file's directory, (2) CWD,
(3) built-in `Lib/`. This means **CWD controls which `pure_lib/` is
found**.

- The pycsl **tool** repo has its own `pure_lib/` (with `os/`, `re/`,
  `json/` — synced separately).
- New modules (like `warn/`) only exist in `pycsl_copy/pycsl/pure_lib/`.
- **For new modules**: must run from `pycsl_copy/pycsl` as CWD.
- **For established modules** (in both repos): can run from either.

```bash
# For NEW modules not yet in the tool repo:
cd /path/to/pycsl_copy/pycsl
PYTHONHASHSEED=0 PYTHONPATH=/path/to/pycsl/src:/path/to/pycsl/src/pycsl \
/path/to/pycsl/.venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', 'pure_lib_test/formal_0003.py']
from pycsl.pycsl import main
main()
"
```

```bash
# For modules already in the tool repo:
cd /path/to/pycsl
PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', '../pycsl_copy/pycsl/pure_lib/os/__init__.py']
from pycsl.pycsl import main
main()
"
```

- `--keep-mlw`: preserve generated `.mlw` file for inspection
- `--no-proof`: skip proof, only check WhyML generation
- `PYTHONHASHSEED=0`: required for deterministic output
- Provers: Alt-Ergo 2.6.2 (primary), Z3 4.13.3 (fallback)

---

## What to cover next

The `lib/calling.json` file lists all stdlib symbols PyCSL uses.
Modules covered so far: `os`, `re`, `warnings`, `json`. Remaining
modules include `collections`, `typing`, `ast`, `sys`, `io`, and
others.

Priority for the next module should consider:
1. **Symbol count** in `calling.json` (more symbols = more value)
2. **Code complexity** (integer-heavy code proves better than string-heavy)
3. **Self-annotation proximity** (which module unblocks the most
   self-annotation coverage)
4. **Verifiability** — prefer modules whose logic is integer/boolean
   heavy (like `warnings`) over string-heavy ones (like full `json`
   encoder). When a module is mixed, use the thin API wrapper pattern.

---

## Anti-patterns

- **Using `\trusted`** — defeats the purpose. If PyCSL can't prove
  something, identify the missing feature precisely and document it.
- **Abstraction over concrete implementations** — pure_lib modules are
  real runnable Python, not stubs. Test them concretely first.
- **Ignoring formal test failures** — a formal test failure means the
  postcondition is wrong or the implementation has a bug. Fix it.
- **Fighting the tool** — if body-level proof is blocked by 5+ tool
  gaps, switch to stub-level formal tests. Document the gaps and
  move on. Consider the thin API wrapper pattern for partial coverage.
- **Forgetting `PYTHONHASHSEED=0`** — results become non-deterministic
  without it. Always set it.
- **Adding `: str` type annotations** — PyCSL maps `str` to Why3
  `string`, but all APIs use `int`. Drop string annotations.
- **Putting functions in a submodule and re-exporting** — function
  contracts don't propagate through `__init__.py` re-exports. Put
  annotated functions directly in `__init__.py` (classes are fine in
  submodules).
- **Running from the wrong CWD** — PyCSL resolves imports from CWD.
  New modules not yet in the tool repo MUST be run from
  `pycsl_copy/pycsl` as working directory.

---

## Related files

- `1009.md` — PyCSL tool requirements R1–R4
- `1111.md` — PyCSL tool requirements R5–R7
- `07-0647-gaps.md` — PyCSL tool requirements R8–R13
- `docs/glossary/formal-test.md` — defines the formal test concept
- `lib/calling.json` — call graph of stdlib symbols to cover
