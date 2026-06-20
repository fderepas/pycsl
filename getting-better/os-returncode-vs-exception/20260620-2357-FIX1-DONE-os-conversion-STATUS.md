# os return-code → OSError: Fix 1 LANDED + os PoC conversion — STATUS

**Branch:** `os-exception-rootcause` (working tree; STOP-AT-PROPOSAL — no commit/push).
**Author:** test-supervise-sl supervisor run.
**Re-verify before merge** — exact commands below. This is NOT a self-report; everything
here is a machine verdict you can reproduce.

---

## 1. Fix 1 (the OSError subclass hierarchy) — NEEDED, IMPLEMENTED, regression-clean

### 1.1 Empirical confirmation it was needed
Probe (`/tmp/probe_oserror.py`): a function raising `FileNotFoundError`, caught by
`except OSError`. On the **clean baseline** Why3 rejects it:

```
File ".../*.mlw", line 21: this expression raises unlisted exception FileNotFoundError
[-] Verification FAILED or INCOMPLETE.
```

i.e. `except OSError` did NOT catch a raised `FileNotFoundError`. Confirmed structurally:
`_handle_try_stmt` emitted one `with <Exc> ->` arm per handler with the literal exc name; no
subclass expansion. **Fix 1 required.**

### 1.2 What was implemented (4 files)

- **`src/pycsl/exception_model.py`** — added `EXCEPTION_BASES` (the OSError family:
  FileNotFoundError, FileExistsError, PermissionError, NotADirectoryError, IsADirectoryError,
  InterruptedError, BlockingIOError, ChildProcessError, ConnectionError, ProcessLookupError,
  TimeoutError, and `error` as the documented OSError alias). Helpers: `bases_closure(exc)`
  (reflexive-transitive ancestors), `handler_catches(handler, raised)`, `subclasses_of`.
  **`OSError` is deliberately kept OUT of `KNOWN_EXCEPTIONS`** (no math trigger; raised on an
  explicit failure condition, the SyntaxError precedent) — per ROOT-CAUSE Fix 1 step 4.

- **`src/pycsl/module6_whyml/stmt_control_flow.py`** — `_handle_try_stmt` now expands each
  handler `except B` into a Why3 `with`/`|` arm for **every concrete tag the body can raise that
  B catches** (B itself + modelled subclasses). The body-raised set includes exceptions raised by
  **called functions** via their declared `#@ raises` (new `_callee_raised_in` / `_callee_raised_direct`,
  try/except- and hierarchy-aware), so an os wrapper whose try-body calls `sys_open` (which raises
  via contract) gets the `FileNotFoundError` arm even with no literal `raise` in the body.

- **`src/pycsl/module6_whyml/ir_scanner.py`** — `collect_escaping_exceptions` made
  hierarchy-aware (an `except OSError` removes a raised `FileNotFoundError` from the escaping set).

- **`src/pycsl/module6_whyml/functions.py`** — the function-level `raises {}` summary:
  (a) `#@ raises OSError` now **summarises** subclass raises — emits a conditioned arm per
  body-raised subclass; (b) the base arm is dropped when it acts purely as a summary (the base
  is not itself in the effect — Why3 rejects `raises {E}` for an E not raised); (c) callee-raised
  exceptions are added to the function's escaping set, **minus** what the function's own
  `#@ no_exception` absurd-wraps (so 0383's pure `let function` emission is preserved).

### 1.3 Acceptance tests (all reproduced)

| Probe | Expectation | Verdict |
|---|---|---|
| `except OSError` catches raised `FileNotFoundError` | SUCCESS | **SUCCESS** |
| `#@ raises OSError` summarises a subclass `raise` (subclass-only body) | SUCCESS | **SUCCESS** |
| `except FileExistsError` (sibling) does NOT catch `FileNotFoundError` | must FAIL | **FAILED** (escapes — hierarchy is precise, not flat) |

### 1.4 Regression status
- **53 exception/raise/no_exception corpus files** (`grep -l "except|try:|raise|no_exception|raises"`):
  **0 regressions** vs `# pycsl-expected` markers.
- One real regression was found mid-development (**0383** — interprocedural `no_exception` vs callee
  `raises`) and **fixed** before this writeup (the `no_exception` absurd-wrap subtraction in
  functions.py). It is GREEN again.
- **Pre-existing, NOT mine:** `bin/run-conformance.sh` front-end IR conformance fails with 38
  MISMATCHes on keys `fresh_globals/propagate_frame/sibling_concrete/verify_module/init_ensures` —
  **identical with my 4 files stashed**, so it is prior branch drift unrelated to the exception
  work. Logged for the parent; not introduced here.

**Reproduce Fix 1:**
```
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl test-suite/corpus/pycsl-reference/0383.py   # SUCCESS
# 0449/0450/0451/0453/0459/0461/0526/0611/0614 SUCCESS; 0460/0462/0612/0613/0615/0644/0687 expected-FAIL
```

---

## 2. os model conversion — PoC: mkdir / rmdir / stat now RAISE (no more `-1`)

Design decision (faithful + minimal-disruption): the **`sys_*` KERNEL layer keeps the Unix
syscall `-1` ABI** (that IS faithful to the kernel), and the **`os.*` wrapper is the
errno→exception translation layer** — exactly as CPython's `os` module is a thin C wrapper that
raises on `-1`. Converted in `src/pycsl_lib/os/__init__.py`:

- **`mkdir`**: `raise OSError` on failure; success establishes presence
  (`ensures dir_lookup(post) >= 0`). Returns None on success (CPython-faithful).
- **`rmdir`**: `raise OSError` on failure; success establishes absence
  (`ensures dir_lookup(post) < 0`).
- **`stat`**: `raise FileNotFoundError when dir_lookup < 0`; returns the inode `[0,32)` on success.

**Per-function verdicts (live tree, `--fun`):**
```
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/pycsl_lib/os/__init__.py --fun mkdir  # SUCCESS
                                                                              ... --fun rmdir  # SUCCESS
                                                                              ... --fun stat   # SUCCESS
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/pycsl_lib/os/__init__.py            # SUCCESS (whole module)
```
- **0 `\trusted`** in the emitted `os/__init__.mlw` (`grep -c trusted` = 0). Additive: the other
  35 functions still verify.

### 2.1 IMPORTANT finding — FileExistsError/FileNotFoundError SUBCLASS refinement is expensive
Distinguishing `FileExistsError` (mkdir on existing) from generic `OSError` requires the wrapper to
**re-query state** (`sys_stat`) after the `-1`, because the kernel collapses all errno to `-1`.
That second syscall's contract bi-conditionals **blow up the VC to Timeout** (mkdir went from 0.01s
Valid → 30s Timeout). So the landed PoC raises **generic `OSError`** on mkdir/rmdir failure (still
faithful: CPython's FileExistsError IS-A OSError, and `except OSError` catches it via Fix 1). `stat`
keeps the precise `FileNotFoundError` because absence is determined by the *same* `ino < 0` it
already branches on — no extra query, no blowup. **Refining mkdir/rmdir to the precise subclass needs
a cheaper errno discriminant from the kernel layer (a follow-on the parent should scope).**

---

## 3. Faithful formal test — `src/pycsl_lib_test/formal_os_raises.py`

Exercises the EXCEPTION path (the counterpart to formal_os_dir.py's `-1` guards):
- `formal_os_stat_present`: mkdir(d); stat(d) → valid inode, no raise. **SUCCESS**, NON-vacuous
  (`ensures False` over `mkdir; stat` → FAILED, i.e. context is consistent).
- `formal_os_stat_absent_raises`: mkdir(d); rmdir(d); `try stat(d) except OSError: return 1` →
  `ensures \result == 1` reached only through the handler catching the raised `FileNotFoundError`.
  Emits + proves **SUCCESS**.

### 3.1 BLOCKER (logged honestly, NOT shipped as green) — module-context vacuity on the rmdir path
The non-vacuity calibration **FAILED** for the *absent* theorem: seeding `ensures \result == 2`
and even `ensures False` over `mkdir; rmdir; try stat …` both **prove SUCCESS** → the post-`rmdir`
context is **VACUOUS** (proves `false`). Bisected:
- `mkdir` alone: `ensures False` → **FAILED** (non-vacuous, sound).
- `mkdir; stat`: `ensures False` → **FAILED** (sound).
- **`rmdir`**: introduces the vacuity (the `ensures False` flips to SUCCESS once rmdir is in the path).

The whole-module `--check-vacuity` gate **FAILS**, flagging `mkdir/rmdir/stat` **alongside the
pre-existing `fstat/lstat`**, with the documented root cause:
> "several nonlinear integer-division facts coexisting in one context … See
> getting-better/csys-vacuity-investigation/ROOT-CAUSE.md."

This is exactly the known nonlinear-div module-context vacuity the mission said to **report rather
than ship vacuous green**.

### 3.2 SETTLED — the module-context vacuity is PRE-EXISTING, NOT introduced by the conversion
I ran the `--check-vacuity` gate against an **isolated git-HEAD copy of the ORIGINAL `-1`-model**
`os/__init__.py` (in `/tmp/os_baseline_pkg/`, live tree untouched):
```
git show HEAD:src/pycsl_lib/os/__init__.py > /tmp/os_baseline_pkg/pycsl_lib/os/__init__.py   # 0 raises
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl:/tmp/os_baseline_pkg .venv/bin/python -m pycsl \
    /tmp/os_baseline_pkg/pycsl_lib/os/__init__.py --check-vacuity --vacuity-timelimit 10
```
**Result — the BASELINE also FAILS the gate:**
```
[-] NON-VACUITY GATE FAILED: the following function(s) verify VACUOUSLY …  (incl. listdir, lseek, scandir, fstat, lstat)
[-] Verification FAILED (vacuous proof).
```
So the os module's `--check-vacuity` failure is **pre-existing** — the documented nonlinear-integer-
division module-context vacuity ([[csys-vacuity-investigation]]), present in the shipped `-1` model
before any exception work. **The conversion did NOT widen it.** It is an honest, prior module-level
GAP routed to the human; my converted mkdir/rmdir/stat are NON-vacuous *per-function*
(`ensures False` over each body individually → FAILED, i.e. consistent — see §3 bisection), and the
present-case formal test is non-vacuous. The *absent*-case formal test rides the rmdir path that
participates in this pre-existing module vacuity, so its non-vacuity cannot be independently
certified until the module-level nonlinear-div vacuity is fixed (a separate, owned bug). Both the
baseline and the converted module are equally affected.

---

## 4. Differential CPython oracle (ROOT-CAUSE Fix 2b) — NOT yet wired
Not implemented this run (time-boxed by the vacuity investigation). The faithful direction is clear
and should be a follow-on: a `bin/` harness running the same failure inputs (mkdir existing, rmdir
absent, stat absent) against real CPython `os` and asserting agreement (CPython raises
FileExistsError/FileNotFoundError; the converted model now raises OSError/FileNotFoundError —
they AGREE on "raises an OSError-or-subclass", DISAGREE on the precise subclass for mkdir/rmdir
until §2.1 is resolved).

---

## 5. Patch surface (working tree, uncommitted)
```
src/pycsl/exception_model.py                  (+ EXCEPTION_BASES, bases_closure, handler_catches, subclasses_of)
src/pycsl/module6_whyml/stmt_control_flow.py  (handler subclass-expansion + _callee_raised_in/_direct)
src/pycsl/module6_whyml/ir_scanner.py         (hierarchy-aware escaping set)
src/pycsl/module6_whyml/functions.py          (raises-summary expansion + no_exception subtraction)
src/pycsl_lib/os/__init__.py                  (mkdir/rmdir/stat: -1 -> raise; PoC only)
src/pycsl_lib_test/formal_os_raises.py        (new faithful exception formal test)
```

## 6. What is DONE vs OPEN
- **DONE (machine-verified, reproduce above):** Fix 1 (hierarchy) + 3 acceptance probes + 53-file
  regression-clean; mkdir/rmdir/stat convert to raise and verify SUCCESS, 0 `\trusted`; the
  present-case formal test is non-vacuous.
- **OPEN / routed to parent (honest GAPs, NOT closed):**
  1. The **module-context nonlinear-div vacuity** (§3.1–§3.2) is **pre-existing** (baseline `-1`
     model fails `--check-vacuity` identically). It is a prior owned bug
     ([[csys-vacuity-investigation]]); the absent-case formal test's non-vacuity rides on it and
     cannot be certified until it is fixed. NOT a conversion regression.
  2. **Precise FileExistsError/FileNotFoundError for mkdir/rmdir** (§2.1) needs a cheaper kernel
     errno discriminant.
  3. The **other ~15 fallible os functions** (open/close/read/write/unlink/chmod/lseek/dup/link/
     rename/symlink/readlink/truncate/listdir/scandir) are **not yet converted** — same pattern
     applies, sequenced after the vacuity blocker is resolved.
  4. The **differential CPython oracle** (Fix 2b) is not wired.
  5. The existing formal_os_*.py tests still assert the `-1` consequence and must be migrated.
