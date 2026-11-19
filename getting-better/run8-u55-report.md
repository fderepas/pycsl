# run #8 executor u55: route #613 follow-up (review rt66 g01 / g02 / g08 / g09 / g10, refusal-only)

Branch `run8-u55`, tree `/home/fabrice/git/pycsl-u55`, base `run8-int69` = ff03f178c. Brief
`scratchpad/run8/brief-u55.md`, plus the driver's added item (`check-stdlib-modules-verify` red at int69)
and two driver decisions: g02 option A, and the `--stdlib` plane mode. Route file:
`getting-better/open-routes/route613-transitive-stdlib-shadow.md` (section "u55 follow-up").
Logs: `/home/fabrice/git/pycsl/scratchpad/u55/logs/` (abbreviated `L/` below).

## 0. Status

- DONE, all gates green; see §5. No new `\trusted` (367). Proof-axiom ledger 3. No gate loosened.
  The two checker edits (stdlib plane mode, corpus-executes loader) are explained in §3 / §5.
- oom_kill was 15 at the start and the end of every job (G1, G2, G3, the proofs and the base
  plane), so no result is VOID.
- **USER-VISIBLE DECISION (§1): the new declared mode `--verification-image`.**

## 1. USER-VISIBLE DECISION: a new declared mode `--verification-image ROOT`

This is driver decision A on g02. The faithful g02 cannot hold for the self-annotation mirror:

- The ROOT-level mirror files (`pycsl.py`, `ir_schema.py`, `core_ir_semantic.py`, ...) resolve
  `errors`, `frontend.*` and `module6_whyml.*` to the MIRROR copies, because their own directory
  comes first.
- The subpackage files (`frontend/*`, `module6_whyml/*`, `proof2why3/*`) resolve the same names to the
  LIVE `src/pycsl` copies, through `--import-path`.
- Every such pair differs (for example `errors.py` by 57 diff lines and `ir_schema.py` by 1663).

So no single `sys.path[0]` reproduces both groups.

- **Meaning.** The file is a verification model that CPython never executes, so the proof makes NO
  claim about a CPython run.
- **What resolves how.** Its own imports resolve as pycsl resolves them: program directory first,
  then `--import-path`. Only the route #613 closure check's roots move to ROOT, and #613 / #611 / r12
  and the u55 g01 / g09 / g10 changes all still apply (witness 10228).
- **Reporting.** `--soundness-report` lists it as VERIFICATION-IMAGE: "NO CPython-RUN CLAIM".
- **Scope.** Opt-in and never inferred (`PYCSL_VERIFICATION_IMAGE`). It excludes `--as-package-module`
  (rc 2), and like that mode it requires ROOT to contain the file.
- **Who uses it.** All 18 mirror-gate scripts that passed `--as-package-module src/self-annotate/src`
  now pass `--verification-image src/self-annotate/src`. The mirror emission is byte-identical
  (§5, D).
- `--as-package-module` is now the user-facing mode only, and it gets the faithful g02 / g08.

## 2. The five gaps: rule, base vs head

CPython evidence is in `L/cpython-witnesses.txt` (both `/usr/bin/python3` and the venv 3.14 interpreter,
`-B`, ulimit). Verdicts are full proofs per memory model (`L/pr-base/`, `L/pr-head/`; oom_kill 15 at every
start and end). Base = ff03f178c (tree `pycsl-u55-base` with the witnesses copied in); head = 3601e6f2b+.
Typed / store VERIFY-FAIL at base is unrelated to the route (the controls 10221 / 10226 fail the same way;
u52 §2 recorded the same).

| case | witness | CPython (`__file__`) | base h / t / s | head h / t / s |
|---|---|---|---|---|
| g02 | 10220 | `python -m pycsl-reference.10220_…` from test-suite/corpus: `r613x_g02.__file__` = test-suite/corpus/r613x_g02.py, "result 2" | PROVED / VF / VF (claim `\result == 1` is FALSE) | REFUSED x3 PACKAGE-MODE-ORDER |
| g02 ctl | 10221 | `json` agrees in both orders (cwd's admitted ./json/) | PROVED / VF / VF | PROVED / VF / VF (G3) |
| g08 | 10222 | runs g08/pycsl-reference/`__init__.py` (marker), then "No module named pycsl-reference.10222_…" | PROVED / VF / VF | REFUSED x3 PACKAGE-MODE-PARENT |
| g01 | 10223 | `_sysconfigdata__linux_x86_64-linux-gnu` loaded from the --import-path root | PROVED / VF / VF | REFUSED x3 TRANSITIVE-SHADOW |
| g01 ctl | 10226 | zoneinfo, no shadow | PROVED / VF / VF | identical (emits) |
| g10 | 10224 | `json.__file__` = r613x/g10/json.py (PYTHONPATH = that root) | PROVED / VF / VF | REFUSED x3 TRANSITIVE-SHADOW (SHADOWS-STDLIB node) |
| g09 | 10225 | /usr/bin/python3: "LOCAL apport package loaded" after the uncaught ValueError; venv: not loaded | PROVED / VF / VF | REFUSED x3 TRANSITIVE-SHADOW |
| image ctl | 10227 | (never run: a model) | rc 2 (no such flag) | PROVED / VF / VF (a program-dir import `multi_file_lib.r613x.g02.r613x_g02c`; the same file under `--as-package-module test-suite/corpus` is REFUSED PACKAGE-MODE-ORDER, `L/ctlq.txt`) |
| image | 10228 | — | rc 2 (no such flag) | REFUSED x3 TRANSITIVE-SHADOW (the closure is still judged) |

The rt66 probes themselves (`/home/fabrice/git/pycsl/scratchpad/u55/probes/`, copies of
`scratchpad/rt66/probes/`), at head, quick (`L/q-head1/`):

- g01, g09, g10 (with `--import-path X`), g02 and g08 (with `--as-package-module root`) are all REFUSED.
- g08 is refused by the dependency rule on the parent `__init__`: `PYCSL-SEM-IMPORT-STATE-MANIPULATED`,
  "`sys.path`".
- In script mode, g02 and g08 still emit, which is correct: CPython then does load the sibling, and does
  not run the parent `__init__`.
- o04 and o05 (bare `email/` and `tkinter/` directories) still emit.
- o01 / o02 (`test/`, `test.py`) and o03 (`pip.py`) stay refused (§4).

### Rules (all inline in `src/pycsl/frontend/ir_resolve.py`; the mirror twins of `_resolve_module_path`,
`resolve_imports` and `main` are `\trusted` with `raises` declared; no helper extracted)

- **g02, `_resolve_module_path`** (absolute branch, `PYCSL-SEM-IMPORT-PACKAGE-MODE-ORDER`). Under
  `--as-package-module ROOT`, when the importing file is not directly in ROOT, the same name is
  resolved again with ROOT in the importer's place, through the same function, so #326 / #611 / r12 /
  #475 judge what ROOT holds. A different file, or a file on one side only, refuses.
  - This covers the program's own imports AND its dependencies' imports, since under -m both resolve
    from `sys.path[0]` = ROOT.
  - An agreeing import emits exactly as before.
  - The rule is skipped under `--verification-image`, and for the closure check's notional entry script.
- **g08, `resolve_imports` top-level** (`PYCSL-SEM-IMPORT-PACKAGE-MODE-PARENT`). Under the mode, for
  `python -m a.b.prog`:
  - `a`, `a.b` and `a.b.prog` must each resolve from ROOT to exactly `a/__init__.py`, `a/b/__init__.py`
    (or no file, for a namespace portion) and the program file. Through `_resolve_module_path`, that
    applies #326 / #611 / r12 (the program's own `__pycache__` and the `__init__` chain's, a residual
    the r12 comment had listed) and #475.
  - Each parent `__init__.py` is then judged as a dependency: the #326 import-system rule on its own
    source (a recursive `resolve_imports(..., _r326_dep)`, as for a dependency), and no dynamic import
    machinery (importlib / imp / zipimport / pkgutil / runpy / `__import__`).
  - Module names may be any path components without a `.`: `python -m py-ref.10220_x` runs (measured).
- **g01** (names). The judged set also contains:
  - every key of the stdlib table;
  - every importable entry of Lib, lib-dynload and platstdlib (plus `plat-*`): a module file (`.py`,
    `.pyc` or extension suffix) or an identifier directory other than `__pycache__`;
  - literal first arguments of `__import__`, `import_module`, `files`, `find_spec`, `run_module` and
    `import_fresh_module` in stdlib source, which adds `tzdata` and `comtypes`. The table key is bumped
    to `r613-v2`.
- **g10** (`resolve_imports`). Each candidate is judged in ITS OWN root, through a notional entry
  script `__pycsl_r613_entry__.py` placed there, instead of `_resolve_module_path(name)` taking the
  first hit in pycsl's order. The namespace-directory rule is applied per root.
- **g09** (`resolve_imports`). The startup-hook closure:
  - Seeds: `sitecustomize` and `usercustomize` in each site directory and the stdlib directory, and
    the `import` lines of every `.pth`.
  - The site directories are `[stdlib] + site.getsitepackages() + site.getsitepackages([sys.base_prefix,
    sys.base_exec_prefix]) + site.getusersitepackages()`, which covers the venv AND the base
    installation's `/usr/lib/python3/dist-packages`.
  - It is followed MODULE BY MODULE: each dotted name goes to its `__init__.py` chain and module file,
    including absolute, relative and literal names, and the walk never enters the stdlib.
  - It reaches 25 top-level names on this host (§4).
  - Cache: `src/pycsl/__pycache__/r613-startup-hooks-<key40>.json`. It is used only while every probed
    path keeps its (size, mtime_ns), or stays absent, and every site directory keeps its listing; when
    that fails it is rebuilt, never failing open.
  - Prototype cost: 3.7 s, once.
  - A whole-package, flow-insensitive variant reached 161 names, including `pkg`, `path`, `mod`, `foo`
    and `parent` from vendored test trees. It was rejected as gross over-refusal.

Warm cost: 1.37 s per `--no-proof` run of 10188 (u52 measured 1.31 s at base and at int69). The first
run in a fresh tree builds both caches (6.42 s). Source: `L/G1/time.txt`.

## 3. The `check-stdlib-modules-verify` item (driver)

- **Before** (ff03f178c, full plane, `L/stdlibplane-base.log`, oom_kill 15 -> 15): 104 modules, 82
  VERIFY, 22 do not (FAILS 3, REFUSED 18, TIMEOUT 1).
- **The only new entry outside BASELINE:** `__init__.py` (REFUSED).
- **Cause: #613.** The program directory `src/pycsl_lib` holds the stdlib-named model packages
  `copyreg/`, `errno/`, `http/`, `json/`, `os/`, `re/`, `reprlib/`, `stat/` and `token/`. Script mode
  would put them on `sys.path`. Neither #612 nor the environment is involved: the other 21 are exactly
  BASELINE, and a quick run gives the same refusals (`L/libq-base.txt`).
- **Fix.** The plane passes `--as-package-module src`. The library is imported as `pycsl_lib.X`
  (pyproject `[tool.setuptools.packages.find] where = ["src"]`, on `sys.path` through the editable
  install's `.pth`). The mode's g02 / g08 rules apply in full.
- **Quick check with the flag** (`L/libq-head-pm.txt`): `__init__.py` passes, and 103 / 104 verdicts are
  identical to script mode.
- **After:** G1 full plane at 4b3c2b767 (`L/G1/P-stdlib.log`, oom_kill 15 -> 15): 104 modules, **83 VERIFY,
21 do not (FAILS 3, REFUSED 17, TIMEOUT 1)**, "OK -- the non-verifying set is the known one (21)", rc 0.
`__init__.py` VERIFIES.

## 4. Over-refusal (measured before any narrowing)

| tree | effect |
|---|---|
| corpus root | 3286 baseline / 3289 candidate .mlw, 0 MOVED, 0 GONE, 0 APPEARED (the +3 are the new controls 10221 / 10226 / 10227) |
| pyref | 2185 / 2185, 0 / 0 / 0 |
| mirror | 53 / 53, `diff -rq` 0 lines, 0 / 0 / 0 |
| pycsl_lib (stdlib plane) | none from u55 (`libq-head1` = `libq-base`); the int69 `__init__.py` refusal is fixed by the declared mode |

So the new names, the per-root judgement, the hooks and the -m rules refuse NO previously emitting
corpus, pyref or mirror file. Nothing was narrowed.

Documented over-refusals, all fail-closed:

- **`test/` or `test.py` beside a program** (rt66 o01 / o02, introduced at int69). It stays refused.
  `test` is a stdlib directory, so g01 requires the name. The only stdlib importer outside `test`
  itself is `multiprocessing.util._cleanup_tests`, and no stdlib code outside `test/` calls it.
  Narrowing on that would be a call-graph argument the table does not make, so it is not done.
- **Names reached only by the hook closure**, which is flow-insensitive within a file: `packaging`,
  `yaml`, `wheel`, `setuptools`, `jaraco`, `platformdirs`, `typing_extensions`, `zstandard`,
  `android`, `jnius`, `backports`, `tomli`, `importlib_metadata`, `importlib_resources`,
  `more_itertools`, `pkg_resources`, `trove_classifiers`, `distutils`, `_distutils_hack`,
  `_manylinux`, `_typeshed`, `apport`, `apport_python_hook`, `problem_report` (host-specific).
- **A program run with `--as-package-module` that imports a sibling by a bare name.** It is refused:
  CPython raises ModuleNotFoundError there.

## 5. Gates (jobG on snapshot `pycsl-u55-g1` @ 4b3c2b767, cwd = tree root, PRIO; `L/G1/`)

- **Byte-diff, corpus root** vs `run8/v68/bd-int` (`C-root.txt`): 3286 baseline / 3289 candidate,
  0 MOVED, 0 GONE, 0 APPEARED. The +3 are the new controls 10221, 10226 and 10227; 9 new sources were
  named with `--new-source`. rc 0.
- **Byte-diff, pyref** (`C-pyref.txt`): 2185 / 2185, 0 / 0 / 0. rc 0.
- **Mirror** vs `run8/v68/mir-int`: 53 emitted, `diff -rq` 0 lines, byte-diff-compare 53 / 53,
  0 / 0 / 0. rc 0. This is with `--verification-image` in place of `--as-package-module`.
- **Fidelity**: sync rc 0, mirror-check rc 0, doc-coherency rc 0.
- **Fast planes**: 61 / 62. The one red was `check-corpus-executes`, whose harness imported a package
  module with an `import` statement and so could not load the 10223 / 10222 fixtures (a dashed,
  computed module name; a `pycsl-reference/` package directory).
  - Fixed in d39798056: the harness now loads by `importlib.import_module`, which loads an identifier
    path exactly as before.
  - Re-run in G2: G2 (snapshot `pycsl-u55-g2` @ d39798056, `L/G2/`) showed the two
    controls 10221 / 10227 failing to load. They imported modules from an `--import-path` root,
    which the harness does not model, so they were rewritten in be3249193.
  - **G3** (snapshot `pycsl-u55-g3` @ be3249193, `L/G3/`; the diff against 4b3c2b767 is that
    checker plus the two controls): check-corpus-executes rc 0 ("every PASS-expected corpus
    file loads"); fast planes **62 / 62 green**, rc 0; doc-coherency rc 0.
  - G3 also proved the rewritten controls: 10221 PROVED (hoare) at base and at head, and 10227
    PROVED (hoare) at head (rc 2 at base, where the flag does not exist). Typed / store
    VERIFY-FAIL on both sides, as for every json control.
- **check-refusal-witness-coverage** rc 0: 483 demonstrated (the two new sites
  PACKAGE-MODE-ORDER / PACKAGE-MODE-PARENT are among them), 5 undemonstrated (ceiling 5), 10
  unmatchable (ceiling 10).
- **check-assigns-writes-survival** rc 0, on the single-underscore emit dir `L/G1/emit_mir`.
- **check-trusted-frame-honesty** rc 0: param not-lowered 86 (= ratchet).
- **check-getattr-erasure** rc 0: DECLARED 0, ABSENT 27, UNKNOWN 75.
- **frontend-only** 38 / 38, **core-only** 38 / 38.
- **count-trusted** rc 0, and grep `#@ \trusted` in the mirror gives 367 (unchanged).
- **Proof-axiom ledger** 3: `proof_axiom_allowlist.py` untouched (`git diff ff03f178c` empty).
- **stdlib-modules-verify**: see §3. Green.
- **oom_kill**: 15 at the start and the end of G1.
- `--slow` was not run (brief).

## 6. Residuals

- **g09, environment.**
  - The hook closure reads the site directories of pycsl's interpreter and its base installation at
    verification time.
  - Not covered: a different interpreter; a `sitecustomize` / `.pth` in a PYTHONPATH- or `.pth`-added
    directory (including the program's own `sitecustomize` on PYTHONPATH, which u52's name already
    covers); the user site when it is disabled at verification time but enabled at run time.
  - Dynamic hook imports of computed names.
- **Platform-specific witnesses.**
  - 10223's file name is x86_64 Linux CPython 3.14's `_sysconfigdata` name. Elsewhere the file is inert
    and the witness emits.
  - 10225 needs an installed hook that reaches `apport`.
- **`--verification-image`** is an honest no-claim mode. Any file may declare it and then proves
  nothing about a CPython run. The soundness report says so.
- The u52 residuals are unchanged: TOCTOU, a writable pycsl install directory (now also for the hooks
  table), and program-chosen dynamic imports.

## 7. Commits and logs

Branch `run8-u55`, not pushed:

- 3601e6f2b: the rules (g01 / g02 / g08 / g09 / g10), `--verification-image` in main(), the
  soundness report and the 18 mirror-gate scripts, docs, and witnesses 10220-10228.
- 90611c046: check-stdlib-modules-verify `--as-package-module src`; AS-PACKAGE-MODULE report text.
- 4b3c2b767: census rows (via `_census_row`, `scratchpad/u52/census.py`) for 10220, 10222-10225 and
  10228; the route613 file section. This is the G1-gated tree.
- d39798056: the check-corpus-executes loader (`importlib.import_module`).
- be3249193: controls 10221 / 10227 rewritten to load as CPython programs. This is the G3-gated tree.
- the report commit (this file).

Logs, under `/home/fabrice/git/pycsl/scratchpad/u55/`:

- `logs/G1/summary.txt` and its files: C-root, C-pyref, D, D-cmp, E-*, F-planes, P-rwc, P-aws, P-tfh,
  P-gae, P-fo, P-co, P-ct, P-stdlib, time.
- `logs/G2/`, `logs/G3/`.
- `logs/stdlibplane-base.log`.
- `logs/pr-base/`, `logs/pr-head/` (3-model proofs; `logs/jobP.txt`).
- `logs/cpython-witnesses.txt` (produced by `tools/cpy-w.sh`).
- `logs/q-head1/` (the rt66 probes, run by `probes/batch-q.sh`).
- `logs/libq-{base,head1,head-pm}.txt`, `logs/census-rows.tsv`, `logs/ctlq.txt`.
- The scripts are in `tools/` (jobP, jobC, jobG, jobG2, jobG3, wq, plane, libq, census, hooks2
  prototype).
- Liveness: `/home/fabrice/git/pycsl-u55/progress.txt`.

Exact commands: `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh <tools/jobC.sh pycsl-u55-g1 | tools/jobG2.sh
pycsl-u55-g2 L/G2 | tools/jobG3.sh pycsl-u55-g3 L/G3>`, with PYTHON_CPU_COUNT=2 and cwd = the tree root.
