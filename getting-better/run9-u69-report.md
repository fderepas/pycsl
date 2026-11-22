# run #9 executor u69: rt78 s1 (INTRODUCED false proof), s7 / o1 over-refusals, #621 attribute-store bypasses t4 / t8

Branch `run9-u69` (tree `/home/fabrice/git/pycsl-u69`), made from `run9-u66` (d77fae692) with `ghost-assign-bc6`
(12b16cabf) merged in (0132f6e4d) before any change. Brief: `scratchpad/run9/brief-u69.md`. Logs are in
`scratchpad/u69/logs/` (written `L/` below), tools in `scratchpad/u69/tools/`, probes in `scratchpad/u69/probes/`.
The probes are copies of the rt76 / u64 / u66 probes, rt78's probes under `rt78/`, and 11 new ones under `u69/`. All
of this is committed except the sweep `.mlw` files, which git ignores (they are on disk under `L/G/{base,h1,h2,h3}`).
oom_kill was 15 at the start and end of every job and on every probe line, so no result is VOID.

Trees (each has the main .venv symlinked):
- `b0` = /home/fabrice/git/pycsl-u69-b0, detached at c115e0a5a (L19).
- `b1` = /home/fabrice/git/pycsl-u69-b1, detached at 0132f6e4d (my branch base). Its src is byte-identical to u66
  b95cb8767: `git diff d77fae692 0132f6e4d -- src bin test-suite docs` is empty.
- `h1` = 9d4da9216: s1 / s7 / s8 / attribute-store rules, BEFORE the o1 narrowing.
- `h2` = 1cc321fd6: adds the o1 narrowing, the docs and witnesses 10405-10408.
- `h3` = 73f47db9d: the FINAL src. It is h2 plus one message change: the package directory in the new message is
  now printed relative to the cwd. Probe and witness verdicts on h3 are identical to h2 (107 lines compared).

## 0. Status

- **s1** (u66 INTRODUCED false proof, route #622) is FIXED faithfully and now REFUSED by the u60 comparison
  (`PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER`). The dependency's own view reads Q/hz78.py and the program's view
  reads P/hz78.py. The dependency's OWN run (`s1-dep`) still proves, and that is faithful: CPython's
  `python P/dep78.py` loads Q/hz78.py. **c1** stays correct (P SUCCESS, CPython 1).
- **s7** (u66 INTRODUCED over-refusal) is REPAIRED by the same model: the program proves again (P SUCCESS,
  CPython 1). `s7-dep` (dep78's own run, cwd P) stays REFUSED by CWD-ROOT, which is correct: CPython
  `python P/dep78.py` raises ModuleNotFoundError.
- **s8** is a NEW finding while fixing s1, and another u66 INTRODUCED false proof. The program imports a symlinked
  dependency P/dep88.py -> ../Q/dep88.py. Its `from hz88 import one` resolves only in P, and P/hz88.py runs an
  import-time writer `zk88.f = lambda: 2` (CPython prints 2). Results: b0 REFUSED (#483), u66 b1 **P SUCCESS
  (false)**, head REFUSED (#483 again).
- **o1** (u66 INTRODUCED over-refusal, #621) is NARROWED: P SUCCESS again, CPython 1. The argument is in
  section 1 (D). Controls o2 / o3 / o4 stay REFUSED; in each, a sibling, the program or a circular import loads the
  submodule.
- **t4 / t8** (PRE-EXISTING #621 bypasses: false proofs at b0 and b1) are now REFUSED by a NEW raise site with the
  same code, `PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND`. Two new probes are refused by the same rule and were
  false proofs at b0 and b1 too: t11 (the store is in a function called at import time) and t13 (the store is in a
  class body).
- **Over-refusal**, measured BEFORE any narrowing (h1): root / pyref / mirror show 0 MOVED / 0 GONE / 0 APPEARED.
  **The GONE list is EMPTY.** h2 and h3 are identical, plus 4 new witness sources.
- **src changes are in two files only:**
  - `src/pycsl/frontend/ir_resolve.py`: only the `resolve_imports` u60 / #621 walk. `_inject_functions` is
    untouched.
  - `src/pycsl/pycsl.py`: only inside `_run_pipeline`, at routes #510 (~line 2126) and #483 (~line 39525).
    `_BODY_EQ_RE`, and everything from it to `def main`, is untouched.
  - The mirror twins `resolve_imports`, `_resolve_module_path` and `_run_pipeline` are all `\trusted` (checked).
- **Invariants held:** no helper extracted; no new `\trusted` (count stays 366); no axiom (ledger stays 3,
  allowlist untouched); no gate edited (the only bin/ change is 2 census rows); no mirror emission moves.

## 1. Rules (all written inline, no helper)

**A. s1: the first-root view rule (u60 walk).** A reached module now shares the program's single view only when
both conditions hold:
- it is in the program's raw directory, and
- its own first root equals the program's first root.

"First root" uses the `_resolve_module_path` rule: the dirname of the file's realpath when the file is a symlink
into another directory. Otherwise both views are resolved and compared, as for any other dependency. This replaces
u66's `_ln622`, which only covered a symlinked PROGRAM. It applies both to the views (`_fr660`) and to the prefix
anchor (`_fa666`). Why this is faithful:
- the dependency's own run (`python P/dep.py`) has sys.path[0] = Q, and that is how its contracts were verified;
- the program's run resolves the dependency's absolute imports from the PROGRAM's first root.

**B. s7: route #510 (pycsl.py, the type-alias export scan).** A dependency's ABSOLUTE from-import is now resolved
with the program file as anchor (`str(args.file)`). Relative imports keep the dependency as anchor. The old
dependency-anchored resolution raised CWD-ROOT from the symlinked dependency's own first root, although the
program's run was faithful.

**C. s8: route #483 (pycsl.py, the import-time closure).** A non-program module's absolute imports are followed
from BOTH anchors, the dependency and the program (a union, so only more modules get judged). With the dependency
anchor alone (Q), #483 missed P/hz88.py, the module CPython actually runs.

**D. o1: #621 narrowing.** CPython rebinds `pkg.b` to the submodule only when something LOADS `pkg.b`. These are
the ways that can happen:
- `import pkg.b`;
- `from pkg.b import ...` or `from .b import ...`;
- a `from pkg import b` / `from . import b` that runs while the attribute is still missing, i.e. code running
  inside `pkg/__init__` before the `def` (any module it imports, transitively);
- a wildcard import with `__all__`;
- a dynamic loader, which is already refused by #326 / #483;
- an attribute store, which is refused by rule E.

The narrowing ADMITTS exactly one undecorated top-level `def b` in `__init__` (any other form of binding keeps the
refusal), and only when every reached module meets two conditions:
1. No import statement spells a module-name component equal to `b`. This covers any `import a.b` and the module
   of any `from a.b import`. Outside the program it also covers every from-import target, `*` included: only the
   program can never run inside `pkg/__init__`.
2. No code reads `<x>.b.<y>`, which pycsl could resolve to the submodule.

Otherwise the candidate is refused as before. So the binding is admitted only when no reached code can load the
submodule, and pkg then behaves as a plain module.

**E. t4 / t8: the attribute-store rule (after the walk; refusal-only, fail-closed).** This applies in every reached
module, the program included, and anywhere in the file: import time, function bodies and class bodies. Each of the
following REFUSES when its attribute NAME is a submodule name of a package the walk met:
- any attribute Store or Del (assignment, aug-assign, for / with targets, `del`), with any receiver;
- a `setattr` / `delattr` whose name is a string literal.

"Package the walk met" means: every prefix directory of a dotted name, the anchor package of a relative import and
the packages up to it, and the directory of a package `__init__`. "Submodule name" means an entry CPython imports
as `pkg.<name>`, as in route #621. Rule E is broader than the brief's import-time-only variant because it also
covers stores in function bodies. Its cost was measured first (h1): 0 GONE.

Docs: u69 paragraphs added next to u66's in `test-suite/annotations.md`, `docs/pycsl-static-semantics-reference.md`
and `docs/pycsl-translational-reference.md`.

## 2. Probes: base b0 (L19) vs u66 b1 vs head h3, with CPython

**How each column was run:**
- **CPython:** `L/cpython-probes.txt` (`tools/cpy.sh`) runs /usr/bin/python3 and the venv's 3.14 with `-B`,
  `ulimit -v 2000000`, cwd /tmp (or the probe's cwd) and PYTHONPATH set to the --import-path root. The two
  interpreters agree on every probe. `L/cpy-p78.txt` holds the rt78 probes.
- **pycsl:** cwd is the tree root unless a cwd is stated. --no-proof (q) and full proofs (P: hoare,
  PYTHON_CPU_COUNT=2, timeout 3600) are in `L/chainB.txt` (b0, b1, h2), `L/chainC.txt` (h3) and
  `L/J-{b0,b1,h2,h3}/`.
- **Tables:** `L/J-table.txt` (b0 / b1 / h2); h3 equals h2.

| probe | CPython | b0 | u66 b1 | head h3 |
|---|---|---|---|---|
| s1 | 2 | P REFUSED (r19) | **P SUCCESS (false)** | P REFUSED (DEPENDENCY-SEARCH-ORDER) |
| s1-dep (dep78's own run) | loads Q/hz78 (1) | P REFUSED | P SUCCESS | P SUCCESS (faithful) |
| s7 (cwd P) | 1 | P SUCCESS | P REFUSED (CWD-ROOT) | P SUCCESS |
| s7-dep (cwd P) | ModuleNotFoundError | P SUCCESS (unfaithful) | P REFUSED | P REFUSED (CWD-ROOT, correct) |
| s7-treecwd / s1f | 1 / 2 | q SUCCESS / q SUCCESS | q SUCCESS / q SUCCESS | q SUCCESS / q SUCCESS (unchanged) |
| s8 (new) | 2 | P REFUSED (#483) | **P SUCCESS (false)** | P REFUSED (#483) |
| c1 | 1 | P REFUSED (r19) | P SUCCESS | P SUCCESS |
| o1 | 1 | P SUCCESS | P REFUSED (#621) | P SUCCESS |
| o2 (new: sibling `from .b import`) | TypeError (b is the module) | P SUCCESS (partial correctness) | P REFUSED | P REFUSED (#621) |
| o3 (new: program `import zu697.b` in a function) | TypeError | P SUCCESS | P REFUSED | P REFUSED |
| o4 (new: circular `from zu698 import b` in d.py) | 2 | P FAILED | P REFUSED | P REFUSED |
| t4 | 2 | **P SUCCESS (false)** | **P SUCCESS (false)** | P REFUSED (new #621 site) |
| t8 | 2 | **P SUCCESS (false)** | **P SUCCESS (false)** | P REFUSED (new site) |
| t11 (new: store in a function called at import) | 2 | **P SUCCESS (false)** | **P SUCCESS (false)** | P REFUSED |
| t13 (new: store in a class body) | 2 | **P SUCCESS (false)** | **P SUCCESS (false)** | P REFUSED |
| t12 (new: store in a function the program calls) | 2 | q REFUSED (rebound-name) | q REFUSED | q REFUSED (new site, earlier) |
| t9 / t10 (new: program-level alias store / setattr) | 2 / 2 | q REFUSED (rebound-name) | q REFUSED | q REFUSED (unchanged) |
| t1 t2 t3 t5 t6 t7 | 2 | q REFUSED | q REFUSED | q REFUSED (t2 / t3 / t7 now by the new site, earlier stage) |
| a1 / a1-noX / a3 / a3-noX | 2 / 2 / 2 / ModuleNotFoundError | q REFUSED | q REFUSED | q REFUSED |

The rt76 / u64 / u66 probes were re-run on all three trees (q for all 32, P for 16). The head verdict is the same
as u66 b1 for every one of them:
- P SUCCESS: r5, r6, r14, r17, x3, v2down, v1f.
- P FAILED: r12.
- P REFUSED: r1, r2, r2d, r2d-dep, v2d, r12c, b21, a22.
- q SUCCESS: r5b, r6-treecwd, r2r-dep.
- q REFUSED: r3, r9, r2s, r7, r8, r2r, r15, r16, w5, v2, x1, x2.

CPython for these probes is as in u66's report (re-measured in `L/cpython-probes.txt`).

**No head SUCCESS where b0 or b1 refused, except the intended repairs.** Each of those matches CPython:
- s1-dep: its own run, CPython loads Q (1).
- s7: 1.
- c1: 1 (u66 improvement).
- o1 and 10407: 1.

## 3. Over-refusal (measured BEFORE any narrowing, then on h2 and on the final src h3)

Each tree is swept with cwd = its root (`tools/S.sh`, NORMAL) and compared once against base b1 (`tools/chainA.sh`,
`chainB.sh`, `chainC.sh`).

| sweep | h1 (pre-narrowing) | h2 | h3 (final) | logs |
|---|---|---|---|---|
| root | rc 0, 3330 / 3330: 0 MOVED / 0 GONE / 0 APPEARED | rc 0, 3330 / 3334: 0 / 0 / 0, 4 new sources | same as h2 | `L/G/C{1,2,3}-root.txt` |
| pyref | rc 0, 2185 / 2185: 0 / 0 / 0 | same | same | `L/G/C{1,2,3}-pyref.txt` |
| mirror (53) | rc 0: 0 / 0 / 0, diff -rq 0 lines | same | same | `L/G/C{1,2,3}-mir.txt`, `L/G/D{1,2,3}-mir.txt` |

On h2 and h3 the 4 new sources are 10407, 10408, zs08dep and zs08hz. **GONE list: EMPTY in all three sweeps, on
every tree.** The narrowing (D) was therefore not needed for corpus cost; it was applied only because the brief
requires the o1 repair when it is sound.

## 4. Witnesses (IDs 10405-10408, inside [10405, 10419])

Full proofs are in `L/chainB.txt` (b0, b1, h2) and `L/chainC.txt` (h3). CPython (both interpreters, from the tree
root, ulimit'd) gives the column below.

| witness | CPython | b0 | u66 b1 | head | header |
|---|---|---|---|---|---|
| 10405_r621x_sibling_submodule_stores_package_attribute_false (t4 shape) | result 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (new site) | FAIL |
| 10406_r621x_subpackage_init_stores_parent_attribute_alias_false (t8 shape, alias, sub-package) | result 2 | SUCCESS (false) | SUCCESS (false) | REFUSED | FAIL |
| 10407_r621o_package_init_def_beside_unimported_submodule_ctl (o1 shape) | result 1 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10408_r622x_plain_dependency_beside_program_absolute_import_ctl (non-symlinked dependency) | result 1 | SUCCESS | SUCCESS | SUCCESS | PASS |

**Helpers** are all in the corpus root, i.e. the program directory:
- `zs05/{__init__,b,c,d}.py`
- `zs06/{__init__,b,c}.py`, `zs06/sub/__init__.py`
- `zs07/{__init__,b}.py`
- `zs08dep.py`, `zs08hz.py`

Helper verdicts:
- b.py / c.py / zs07 / zs08 full-prove SUCCESS on b0, b1 and h3.
- zs05/__init__, zs05/d.py, zs06/__init__ and zs06/sub/__init__ are REFUSED on their OWN runs on every tree. This
  is correct and pre-existing for d.py / sub (the rebound-name rule), since their own runs do rebind the attribute.
  They carry no header.
- check-corpus-executes loads every helper (rc 0).

**Census:** the real `_census_row` was run on 10405 and 10406 (`tools/CR.sh`, cwd-relative paths). Both rows are
appended to `bin/refusal-witness-census.tsv` (`L/CR-rows3.tsv`, from the final src).

**Rule 38:**
- Full IDs are unique.
- The 4-character cut was already far from empty before u69 (0211..1038, r613, zpy6, zq80).
- u69 adds `1040` (10405-10408 vs 1040_route40_*) and `zs08`, the same kind of artefact u64 / u66 added.
- s1 / s7 / s8 / c1 stay probes, because the corpus holds no symlinks.

## 5. Gates (final src 73f47db9d + census rows; `tools/chainC.sh` -> `tools/GATES.sh`, cwd = u69 tree root, one NORMAL job)

| gate | result | log |
|---|---|---|
| byte-diff root / pyref vs b1 | rc 0 / rc 0, 0 MOVED, 0 GONE, 0 APPEARED | `L/G/C3-root.txt`, `L/G/C3-pyref.txt` |
| mirror sweep 53 + diff -rq | rc 0, 0 lines | `L/G/C3-mir.txt`, `L/G/D3-mir.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency --check | rc 0 / 0 / 0 | `L/GATES/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast + conversion tier, full tee) | rc 0, 62 / 62 green | `L/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 490 demonstrated (u66: 489; +1 = the new site), 5 undemonstrated (ceiling 5) | `L/GATES/rwc.txt` |
| check-corpus-executes | rc 0: 2647 / 2655 load (the 8 failures are the KNOWN ones), 1708 / 1708 self-checks | `L/GATES/ce.txt` |
| frontend-only-conformance | rc 0: 38 OK / 0 MISMATCH | `L/GATES/foc.txt` |
| check-dropped-mutation | rc 0: 0 dropped / 49 ctxbind / 5 tryfinal (ratchet 5) / 0 dangling | `L/GATES/cdm.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `L/GATES/lg/mir_emit`, 53, single-underscore naming) | `L/GATES/lg/*.txt` |
| \trusted | 366 | `L/chainC.txt` [LG] |
| ledger | 3 (no allowlist / axiom change; `git diff 0132f6e4d HEAD -- src bin` = ir_resolve.py, pycsl.py, 2 census rows) | -- |

## 6. Commits (branch run9-u69, not pushed)

- 0132f6e4d: merge ghost-assign-bc6 (setup).
- 9d4da9216: WIP with rules A / B / C / E, probes and tools.
- 1cc321fd6: o1 narrowing (D), docs, witnesses 10405-10408, chainA logs.
- 73f47db9d: relative package path in the new message; chainB logs.
- final: census rows, chainC / gate logs, this report.

## 7. Open / for the driver

- **Other dependency-anchored absolute resolutions remain** in the program's run:
  `_find_record_type_from_dep_imports` (ir_resolve ~line 2181) and the route #613 closure helpers. They only
  matter where u60 admits (the dependency's own view is none / refused). Not probed; possibly worth a red-team
  look in the s8 shape.
- **Rule E is name-based and fail-closed.** Any `obj.<name> = ...` is refused when `<name>` is a submodule of a
  met package, including `self.<name>` in unrelated classes. Corpus cost is 0, but users may hit it; the message
  names the package directory.
- **V1D (the u61 admission of none / refused dependency views) is unchanged.** s7's program proof rests on
  dep78's contract while dep78's own run is refused (the premise is unproved, as for r3 / r9 at base).
- The h1 / h2 trees were removed. b0 / b1 / h3 are kept at the paths above for re-proof.
