# OPEN ROUTE #326 — MODULE RESOLUTION DIFFERS FROM CPython's (shadowing stdlib modules, package vs module, sys.path) — even under --verify-imports
**Status: REPAIRED (gen #37, 2026-10-24; candidate, r326 executor off 0da66911 — see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 19; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r326/`: a local `math.py`/`time.py`/`os.py` next to the script is resolved by pycsl, but CPython always uses its
built-in / frozen / startup-loaded module (shadow/sh01-sh04); with both `dup19/__init__.py` and `dup19.py`, CPython loads the PACKAGE, pycsl the
.py (k04, k05); after `sys.path.insert(0, ".../alt")` CPython imports `alt/sp19.py`, pycsl the script-dir copy (k06). The wrong module itself
verifies, so --verify-imports does not help. Mechanism: `_resolve_module_path` (frontend/ir_resolve.py).
Repair: model CPython's lookup order (sys.builtin_module_names + frozen + startup-loaded stdlib names are never shadowed; package before
module) or refuse when ambiguous (a local file shadowing a stdlib/builtin module name; both pkg and module present); refuse any sys.path /
sys.modules / importlib manipulation in the verified program.

## REPAIR (2026-10-24, r326 executor off 0da66911; commits 61c98f12, d89ee890 (code + witnesses), 38757ff2 (census rows), dfc5305d (mirror stub `raises`), 59b17e74 (docs), 7fb6adc8 (CTXBIND fix) + route docs)
All inline in `src/pycsl/frontend/ir_resolve.py` (`_resolve_module_path` and its caller `resolve_imports`; no new def/field; both
mirror twins are `\trusted`, the `_resolve_module_path` stub now declares `#@ raises PyCSLSemanticError when True`). Ledger 3.

**Rules.**
1. **Package before module** (both branches): inside one root `X/__init__.py` is taken before `X.py` — CPython's `FileFinder` order.
2. **Stdlib shadowing refused** (`PYCSL-SEM-IMPORT-SHADOWS-STDLIB`): an absolute import whose top-level name is in
   `sys.stdlib_module_names | sys.builtin_module_names` and that resolves to a local file in ANY root (script dir, cwd, `src/`,
   `--import-path`) is refused, unless the local file (or, for a package, every `.py` under it) is byte-identical to the running
   interpreter's `sysconfig.get_paths()["stdlib"]` source — then it IS the module CPython runs and resolution is unchanged.
3. **Import-state edits refused** (`PYCSL-SEM-IMPORT-STATE-MANIPULATED`, in `resolve_imports`, main program and, through the same
   check applied to each locally-resolved dependency's own tree, dependencies' top-level code): any reference to `sys.path` /
   `sys.modules` / `sys.meta_path` / `sys.path_hooks` / `sys.path_importer_cache` through any `sys` alias, `from sys import` of one of
   them (or `*`), or the `sys` module object used as a value (`s = sys`, `getattr(sys, ...)`); EXEMPT: pure reads (`len(..)`,
   `isinstance(..)`, `hasattr(sys, ..)` first argument, `k in` / `not in` comparator) and, in the program only, the idempotent
   `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` (prepends pycsl's own first root; the mirror `pycsl.py` uses it).
   Dynamic-import machinery (`importlib`, `imp`, `zipimport`, `pkgutil`, `runpy`, `__import__`) is refused when the program also has
   an import pycsl resolves to a local file (172 python-reference `stdlib/importlib` catalogue files import `importlib` with no local
   resolution and stay emitted).

**Census of stdlib-named local modules** (static walk of every level-0 import in test-suite/, src/self-annotate, src/pycsl_lib,
src/pycsl_lib_test, resolved with the base resolver from the repo root): exactly ONE population outside the route witnesses —
the repo-root `json/` package (cwd root), resolved by 33 python-reference `stdlib/json` + `stdlib/jsonschema` files, 8
agent-tests/cmmi-regression/runner files and 6 mirror files (`pycsl.py`, `frontend/ir_resolve.py`, `frontend/Module5_IREmitter.py`,
`Module6_WhyMLTranspiler.py`, `audit_proof_reverify.py`, `proof2why3/extract_lean_meta.py`). Decision: ADMITTED — all six files are
byte-identical to `/usr/lib/python3.14/json` (it is CPython's own source, not a user stub). `src/pycsl_lib/{copyreg,errno,http,json,os,
re,reprlib,stat,token}/` are shims under the `pycsl_lib.` prefix (top-level name `pycsl_lib`, not shadowing); `lib/`, `attic/` are
not search roots; `src/pycsl/module6_whyml/types.py` (and its mirror) is only imported relatively. Package+module pairs: none in the
repo outside `witnesses-r326/dup19` (rule 1 is corpus-inert).

**Probe table** (base = 0da66911 worktree; after = d89ee890, behaviour-identical at 7fb6adc8; full proofs via heavy.sh; route witnesses with `--verify-imports`):

| witness | CPython | base | after |
|---|---|---|---|
| shadow/sh01 `import math` local math.py | violates | PROVED | REFUSED (SHADOWS-STDLIB) |
| shadow/sh02 `import time` (built-in) | violates | PROVED | REFUSED |
| shadow/sh03 `import os` (startup-loaded) | violates | PROVED | REFUSED |
| shadow/sh04 `from math import floor` | violates | PROVED | REFUSED |
| k04 / k05 package vs module | violates | PROVED | FAIL |
| k06 `sys.path.insert` | violates | PROVED | REFUSED (STATE-MANIPULATED) |
| 4280-4283 shadow math / from math / time / os (`--import-path` root) | violate | PROVED | REFUSED |
| 4284 / 4285 package vs module (from / qualified) | violate | PROVED | FAIL |
| 4286 package contract (control) | ok | FAIL | PROVED |
| 4287 `sys.path.insert` / 4288 `from sys import path` / 4289 `_s = sys; _s.path.insert` | violate | PROVED | REFUSED |
| 4290 `sys.modules.update` in a `\trusted` helper | violates | PROVED | REFUSED |
| 4291 `importlib.import_module` of a module that rebinds `sys.modules` | violates | PROVED | REFUSED |
| 4292 dependency's top level rebinds `sys.modules` | violates | PROVED | REFUSED |
| 4293 idempotent script-dir insert (control) | ok | PROVED | PROVED |
| 4294 `sys.stdout`/`sys.argv` beside a local import (control) | ok | PROVED | PROVED |
| 4295 pure reads `len(sys.path)`, `in sys.modules`, `hasattr`, `isinstance` (control) | ok | PROVED | PROVED |

**Blast radius / gates** (rc captured per leg, logs under the worktree's `.r326tmp/`, deleted at the end):
- corpus byte-diff (chunked replica of `byte-diff-sweep.sh`, base 0da66911 vs after d89ee890 and again at 7fb6adc8): root 2187 / 2193, **0 MOVED, 0 GONE,
  0 APPEARED** (6 new sources ignored) rc=0; pyref 2186 / 2186 **0 / 0 / 0** rc=0 (the first cut refused pyref 0115-0118 — pure
  reads of `sys.modules` / `sys.meta_path` / `hasattr(sys, ..)` — hence the pure-read exemption; M1: zero movers).
- mirror-emit-sweep base vs after (`--min-files 50`): 53/53; 1 MOVED, `frontend__ir_resolve.mlw` (+1 line, `raises { PyCSLSemanticError
  -> true }` on the trusted stub `val`), rc=0 with `--expect-moved frontend__ir_resolve`; L3-tc rc=0; whole-file proof of `src/self-annotate/src/frontend/ir_resolve.py` rc=0 ("All contracts formally proven") — nothing OWED.
- check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53/53); doc-coherency --check rc=0;
  check-assumed-facts rc=0 (85 facts, reviewed families); check-trusted-raises-honesty rc=0 (18 declared / 61 silent, ratchet 61;
  was 62 > 61 before the mirror stub declared `raises`).
- check-refusal-witness-coverage (no flags) rc=1 at BOTH base and after: 6 > 5 unwitnessed, the same six pre-existing sites
  (exec_splice:62, ir_inline:502, expressions:1352, statements:5210, pycsl.py:6195, pycsl.py:1287); the two new sites are
  DEMONSTRATED (302 -> 304 sites, 272 -> 274 demonstrated) by 12 new census rows (4280-4292) produced by `_census_row`.
- run-soundness-planes.sh (fast) at 7fb6adc8: 60/61, the one RED is check-refusal-witness-coverage (pre-existing, above). The first
  run at dfc5305d was 59/61: check-dropped-mutation CTXBIND 52 > 51 (the dependency scan's `with open(dep) as f`), fixed in 7fb6adc8
  (explicit open/read/close; dropped-mutation rc=0, 51/51). check-stdlib-modules-verify rc=0 (104 modules, the known 21 non-verifying).
- Ledger 3, no gate loosened, no helper/nested def added in `src/pycsl`.

**Residuals.** (a) A dependency-of-a-dependency that edits import state is seen only under `--deep` (the dependency scan is one
level; `--deep` re-runs `resolve_imports` on each dependency). (b) Import-state edits reached without the `sys` name or a
dynamic-import module name in the program (e.g. `builtins.__dict__`, `vars(...)`, a C extension) and dynamic machinery with NO local
resolution (it can still rebind a stdlib name pycsl models, e.g. `importlib.import_module("sys").modules["math"] = fake`) are not
refused by this route (existing module-scope write checks catch the direct forms). (c) The byte-identity admission assumes the
target interpreter is the one running pycsl (same assumption as `sys.stdlib_module_names`). (d) The working directory remains a
pycsl search root though CPython does not put it on `sys.path` for `python script.py` (a non-stdlib name found only in cwd still
resolves; an import CPython would fail with `ModuleNotFoundError`).
