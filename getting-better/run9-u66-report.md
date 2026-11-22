# run #9 executor u66: narrow u64's V2D (rt76 r5 / r14 / r6), routes #621 and #622 (refusal-only, import resolver)

Branch `run9-u66` (tree `/home/fabrice/git/pycsl-u66`), created from `run9-u64` (aec1296fe) with
`ghost-assign-bc6` (3bf3f3f21) merged in (2b1c290cf) before any change. Brief `scratchpad/run9/brief-u66.md`.
Logs `scratchpad/u66/logs/` (written `L/` below), tools `scratchpad/u66/tools/`, probes `scratchpad/u66/probes/`
(copies of rt76's `probes/rt76/`, u64's `probes/u64/`, plus 3 new ones in `probes/u66/`). All committed except the
sweep `.mlw` emissions (git-ignored, on disk under `L/G/{base,h1,h2}/`). oom_kill 15 at the start and end of every
job; no result is VOID.

Trees: `b0` = /home/fabrice/git/pycsl-u66-b0, detached at ghost-assign-bc6 3bf3f3f21 (src == original base
2873a902d). `b1` = /home/fabrice/git/pycsl-u66-b1, detached at 2b1c290cf (u64 V2D + merge, before my change).
`h2` = /home/fabrice/git/pycsl-u66-h2, detached at b95cb8767 = the final src / docs / corpus state (later commits:
logs + this report only). (`h1` = 0c6fc7b37 was the first state; its gate run was VOIDED, see section 5.)

## 0. Status

- A (u64's INTRODUCED over-refusals): REPAIRED. r5, r14, r6 PROVE again (as at base; CPython "result 1").
  v2d / w5 / v2 / x1 / x2 and witnesses 10340 / 10341 / 10343 stay REFUSED.
- B (route #621, r2 / r2d, PRE-EXISTING false proof): REFUSED by the new raise site
  `PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND` -- program form r2, dependency form r2d, and the dependency's OWN run
  r2d-dep (which proved its false claim at base).
- C (route #622, r12, PRE-EXISTING false proof): fixed FAITHFULLY: the first root of an absolute import is the
  directory of the file's realpath (CPython's sys.path[0]). r12 now reads X/zz76.py as CPython does and its false
  claim FAILS. A new variant r12c (r12 run with cwd = the link directory) was a base false proof; now REFUSED by
  the existing CWD-ROOT rule (the link directory is no longer exempt).
- Over-refusal measured BEFORE any narrowing: root / pyref / mirror 0 MOVED, **0 GONE**, 0 APPEARED. No narrowing.
- Only `src/pycsl/frontend/ir_resolve.py` changed in src (twins `_resolve_module_path`, `resolve_imports` are
  `\trusted`, checked). pycsl.py not touched (so neither `_run_vacuity_gate` nor `_BODY_EQ_RE`..`def main`).
  No new `\trusted` (366), no axiom (ledger 3), no gate/tool edited (bin/: 1 census row), no mirror emission moves.

## 1. Rules (inline, no helper)

A1 (rt76 r5 / r14; u60/u61 DEPENDENCY-SEARCH-ORDER block, V2D prefix check). CPython imports the submodule
`pkg.name` of `from pkg import name` only when the attribute lookup fails, and pycsl's `_resolve_direct_imports`
always takes `name` from pkg's file, never a submodule. A name that no import statement of the module spells as a
module (not `import a.b`, not the `a.b` of `from a.b import c`, nor a prefix of these; set `_mod666`) skips the V2D
prefix check when pkg (resolved in CPython's roots, A2) is a MODULE file, or a package `__init__.py` binding `name`
in a top-level `def` / `class` / `Assign` / `AnnAssign`-with-value / `import` / non-wildcard from-import with no
`del` / `global` / `nonlocal` of it anywhere. Namespace / unresolved / refused pkg, or an `__init__` without the
binding: checked as before. Module names: unchanged.

A2 (rt76 r6). Why the walk consulted the cwd: it calls `_resolve_module_path`, whose roots are
`[program dir, os.getcwd(), src/, Lib/, --import-path...]`; P/zc76 is a bare (namespace) directory, so the prefix
`zc76` fell through to cwd C/zc76/__init__.py -> CWD-ROOT. Fix: every V2D prefix resolution, and the u60 views of
a PREFIX the V2D expansion added (not spelled by the module), run with the cwd temporarily set to the anchor's first
root (`os.chdir`, restored on every exit; already searched first, so the cwd root is a no-op and CWD-ROOT-exempt).
Names the statements spell keep today's resolution: the CWD-ROOT refusal stays where it was before u64. `src/` /
`Lib/` stay (pycsl's model roots, used by the full-name resolution the check compares against).

B (route #621; same walk, script mode only like V2D). For every package `__init__.py` the program reaches (not the
program itself): its submodules = entries of its directory CPython imports as `pkg.<name>` (module file / artifact
`.py .pyc .pyd .so` + extension suffixes, or an identifier sub-directory, regular or namespace). Its import-time code
(outside def / lambda / class bodies; decorators, defaults, bases, keywords included) is REFUSED when it binds a
submodule's name in any form (import / import-as, from-import / -as, any Store / Del Name: assignment, aug-assign,
for / with targets, walrus, comprehension targets (conservative), `del`; except-name; match captures; def / class
name), has a wildcard import while the package has submodules, or declares the name `global` / `nonlocal` anywhere
-- except `from . import <name>` (exactly that submodule).

C (route #622; `_resolve_module_path` absolute branch). `_fr622` = dirname(realpath(file)) when it differs from
realpath(dirname(abspath(file))) (the file itself is a symlink into another directory); otherwise the spelling is
unchanged (symlinked parent directories keep their strings). The CWD-ROOT exemption list uses `_fr622` instead of
both dirname(abspath) / dirname(realpath) (equal for a non-symlink), so the link directory is no longer exempt. In
the u60 walk a module in the same raw directory as a symlinked program no longer shares the program's view
(`_ln622`). rt62 r19 kept. Residual: the G5 namespace rule still lists the link directory among "other roots"
(conservative over-refusal only).

Docs: A / B / C paragraphs in `test-suite/annotations.md`, `docs/pycsl-static-semantics-reference.md`,
`docs/pycsl-translational-reference.md` (next to u64's V2D text).

## 2. Probes: base b0 vs u64 b1 vs head (h2), CPython

CPython: `L/cpython-probes.txt`, `L/cpython-probes-u66.txt` (`tools/cpy.sh`: /usr/bin/python3 and venv 3.14, -B,
ulimit -v 2000000, cwd /tmp or the probe's cwd, PYTHONPATH = --import-path root); both interpreters agree except r4.
pycsl (cwd = tree root unless stated): --no-proof `L/q-b0.txt`, `L/q-b1.txt`, `L/q-h1.txt`, `L/chain2.txt` [qh2];
full proofs (hoare, PYTHON_CPU_COUNT=2, timeout 3600) `L/chain2.txt` [J] (b0 + h2; `tools/J.sh`), `L/J2.txt` (b1).
P = full proof, q = --no-proof.

| probe | CPython | b0 | u64 b1 | head |
|---|---|---|---|---|
| r2 | 2 | P SUCCESS (false) | P SUCCESS (false) | REFUSED (#621) |
| r2d | 2 | P SUCCESS (false) | P SUCCESS (false) | REFUSED (#621) |
| r2d-dep (dep's own run) | -- | P SUCCESS (false claim) | P SUCCESS | REFUSED (#621) |
| r12 (symlinked program) | 2 | P SUCCESS (false) | P SUCCESS (false) | P FAILED (reads X/zz76.py like CPython; contract gone from `L/q-h1/r12.mlw`) |
| r12c (new; cwd = link dir) | 2 | P SUCCESS (false) | P SUCCESS (false) | REFUSED (CWD-ROOT) |
| r5 | 1 | P SUCCESS | REFUSED (V2D) | P SUCCESS |
| r14 | 1 | P SUCCESS | REFUSED (V2D) | P SUCCESS |
| r6 (cwd C) | 1 | P SUCCESS | REFUSED (prefix CWD-ROOT) | P SUCCESS |
| r6-treecwd | 1 | q SUCCESS | q SUCCESS | q SUCCESS |
| r5b | AttributeError | q SUCCESS (P FAILED, rt76) | REFUSED | q SUCCESS (as base) |
| r1 | 2 | P FAILED | P FAILED | REFUSED (#621) |
| r3 / r9 / r2r | 2 | q SUCCESS (unproved premise) | q SUCCESS | REFUSED (#621) |
| r2r-dep | ImportError | q SUCCESS | q SUCCESS | q SUCCESS (unchanged) |
| r2s | 2 | REFUSED (#483) | REFUSED | REFUSED (#621, earlier stage) |
| r7 / r8 / r4 / r15 / r16 | 2 / 2 / venv MNFE, usr 1 / 2 / 1 | REFUSED | REFUSED | REFUSED (r16 pre-existing over-refusal) |
| r17 control | 1 | P SUCCESS | P SUCCESS | P SUCCESS |
| v2d | 2 | P SUCCESS (false) | REFUSED | REFUSED |
| w5 / v2 / x1 / x2 | 2 / 2 / 2 / MNFE | q SUCCESS / REFUSED / REFUSED / q SUCCESS | REFUSED | REFUSED |
| x3, v2down controls | 1 | P SUCCESS | P SUCCESS | P SUCCESS |
| v1f | 2 | P SUCCESS (false) | P SUCCESS | P SUCCESS (OPEN, u64 section 4; not in this brief) |
| b21 (new: `from .b import b` in __init__) | 1 | P FAILED | P FAILED | REFUSED (#621, conservative) |
| a22 (new: __init__ defines then `del b`) | ImportError | REFUSED | REFUSED (V2D) | REFUSED (V2D still applies) |

No head SUCCESS where base or u64 refused.

## 3. Over-refusal (measured BEFORE any narrowing, and again on the final src)

Base sweep b0 (`L/G/S-base.txt`); head sweeps h1 (`L/G/chain1.txt`, 0c6fc7b37 = pre-narrowing state) and h2
(`L/chain2.txt`, final src b95cb8767); `tools/S.sh`, cwd = each tree root, NORMAL; compared once per tree.

| sweep | h1 (pre-narrowing) | h2 (final) | logs |
|---|---|---|---|
| root | rc 0, 3325 / 3329, 0 MOVED / 0 GONE / 0 APPEARED, 4 new sources | rc 0, 3325 / 3330, 0 / 0 / 0, 5 new sources (10344 from u64, 10381-10383, zq80.py) | `L/G/C1-root.txt`, `L/G/C2-root.txt` |
| pyref | rc 0, 2185 / 2185, 0 / 0 / 0 | rc 0, 2185 / 2185, 0 / 0 / 0 | `L/G/C1-pyref.txt`, `L/G/C2-pyref.txt` |
| mirror (53) | rc 0, 0 / 0 / 0, diff -rq 0 lines | rc 0, 0 / 0 / 0, diff -rq 0 lines | `L/G/C{1,2}-mir.txt`, `L/G/D{1,2}-mir.txt` |

GONE list: EMPTY in all three. No narrowing was applied.

## 4. Witnesses (IDs 10380-10383, inside [10380, 10399])

Full proofs `L/chain2.txt` [J] (b0, h2) and [Jb1] (b1); CPython both interpreters, from the tree root.

| witness | CPython | b0 | u64 b1 | head | header |
|---|---|---|---|---|---|
| 10380_r621_package_init_rebinds_submodule_name_false (#621 program form) | result 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (#621) | FAIL |
| 10381_r621_package_init_binds_submodule_itself_ctl | result 1 | SUCCESS | SUCCESS | SUCCESS | PASS |
| 10382_r613y_from_import_module_attribute_beside_namespace_ctl (r5 shape) | result 1 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10383_r613y_from_import_package_attribute_later_root_submodule_ctl (r14 shape, --import-path B14) | result 1 (with and without PYTHONPATH) | SUCCESS | REFUSED | SUCCESS | PASS |

Helpers (corpus root): `zr80/{__init__,b,c}.py`, `zr81/{__init__,b}.py`, `zq80.py`, `zq80/b.py`
(`# pycsl-flags: --no-proof`: its dotted name cannot load because zq80 is a module -- the r5 shape itself; the
plane skips it), `zh80/__init__.py`; `multi_file_lib/u66/B14/zh80/{__init__,b}.py`. Every helper full-proves
SUCCESS on b0 / b1 / h2 (zq80/b.py: --no-proof SUCCESS); all load with `importlib.import_module` from the corpus
root under CPython.
Route #622 witness: kept as probes `scratchpad/u66/probes/rt76/r12` and `scratchpad/u66/probes/u66/r12c`. The
corpus has no symlink (`find test-suite -type l` empty) and a symlinked witness would put its target `.py` into
every sweep as a second witness; none added.
Census: real `_census_row` on 10380 (`tools/CR.sh`, cwd-relative) appended to `bin/refusal-witness-census.tsv`
(65119ed70); re-run on the final src: byte-IDENTICAL (`L/CR-row2.tsv`, `L/chain2.txt` "CR rc=0 ... IDENTICAL").
Rule 38: full-ID uniqueness unchanged (only pre-existing `r613z`); the 4-character cut gains `1038` (10380-10383
vs 1038_route40_*) and `zq80` (zq80.py + zq80/), the same cut artefacts the driver accepted for u64.

## 5. Gates (final src b95cb8767; `heavy.sh bash tools/chain2.sh`, NORMAL, gates part = `tools/GATES.sh`, cwd = u66 tree root)

| gate | result | log |
|---|---|---|
| byte-diff root / pyref vs b0 (ghost-assign-bc6 tip) | rc 0 / rc 0, 0 GONE, 0 MOVED (section 3) | `L/G/C2-root.txt`, `L/G/C2-pyref.txt` |
| mirror sweep 53 + diff -rq | rc 0, 0 lines | `L/G/C2-mir.txt`, `L/G/D2-mir.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency --check | rc 0 / 0 / 0 | `L/GATES/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast, full tee) | rc 0, 62 / 62 ok | `L/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 489 demonstrated (u64: 488; +1 = the #621 site), 5 undemonstrated (ceiling 5) | `L/GATES/rwc.txt` |
| check-corpus-executes | rc 0: 2633 / 2641 load, the 8 failures are the KNOWN ones; 1706 / 1706 self-checks | `L/GATES/ce.txt` |
| frontend-only-conformance | rc 0: 38 OK / 0 MISMATCH | `L/GATES/foc.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `L/GATES/lg/mir_emit`, single-underscore naming) | `L/GATES/lg/*.txt` |
| \trusted | 366 | `L/chain2.txt` [LG] |
| ledger | 3 (`proof_axiom_allowlist.py` untouched; `git diff 3bf3f3f21 HEAD -- src bin` = ir_resolve.py + 1 census row) | -- |
| new corpus files: full verdict == header | 4 / 4 witnesses; helpers SUCCESS | section 4 |

VOIDED first gate run (`L/GATES-void1*`, on 65119ed70): it found two REDs, both mine and both fixed in b95cb8767:
check-dropped-mutation TRYFINAL ratchet 8 > 5 (my three `try ... finally: os.chdir(...)` blocks; rewritten as
`except BaseException: os.chdir(...); raise` + a plain restore) and check-corpus-executes (10383 did not load:
the plane runs a witness without its --import-path; helpers moved to the program directory, 10382 likewise). I
edited the tree while that run was still going, so I killed it (own task, parent chain checked) and re-ran
everything on b95cb8767 (`L/chain2.txt`).

## 6. Commits (branch run9-u66, not pushed)

- 2b1c290cf merge ghost-assign-bc6 (setup)
- 0c6fc7b37 WIP: rules A / B / C, docs, witnesses 10380-10383, probes, quick logs
- 65119ed70 census row 10380, J logs, sweep compares
- b95cb8767 chdir restore without try/finally; 10382 / 10383 helpers in the program directory
- final: gate logs + this report

## 7. Open / for the driver

- v1f still PROVES (u64 section 4; not in this brief).
- #621 is broad by the brief's spec: `from .core import core` beside `core.py` is now refused (b21: base could not
  prove it either). Corpus / pyref / mirror cost was 0.
- `os.chdir` inside the resolver is process-global (front end single-threaded, restored on every exit); a root-list
  parameter on `_resolve_module_path` would be cleaner but changes a mirrored signature.
- G5 namespace rule still lists the link directory of a symlinked program (conservative).
