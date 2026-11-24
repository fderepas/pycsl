# run #9 executor u71: rt79 r1 (rule E over-refusal), route #626 (wildcard `__all__` submodules), route #627 (zip on --import-path)

Branch `run9-u71` (tree `/home/fabrice/git/pycsl-u71`), made from `run9-u69` (ed039ebcb) with `ghost-assign-bc6`
merged in (f536b181f) before any change. Brief: `scratchpad/run9/brief-u71.md`. Logs: `scratchpad/u71/logs/` (`L/`
below), tools: `scratchpad/u71/tools/`, probes: `scratchpad/u71/probes/` (copies of the rt76 / rt78 / u64 / u66 /
u69 / rt79 probes plus 12 new ones under `u71/`). Sweep `.mlw` files are git-ignored (on disk under `L/G/`).
oom_kill was 15 at the start and end of every heavy job and on every probe / witness line (399 / 399): no result VOID.

Trees (each with the main .venv symlinked; all kept for re-proof):
- `b0` = /home/fabrice/git/pycsl-u71-b0, detached at c115e0a5a (L19).
- `b1` = /home/fabrice/git/pycsl-u71-b1, detached at 73f47db9d (u69 final src; the base of every sweep compare).
- `h1` = /home/fabrice/git/pycsl-u71-h1, e580aae79: #626 + #627, BEFORE the rule E narrowing (the over-refusal measure).
- `h2` = /home/fabrice/git/pycsl-u71-h2, 08e65645c: FINAL src (+ narrowing, docs, witnesses). Later commits change
  only logs, the census TSV and this report.

## 0. Status

- **r1** (u69 INTRODUCED over-refusal) REPAIRED: head P SUCCESS, CPython 4 (= claim). t4 / t8 / t11 / t13 and
  witnesses 10405 / 10406 stay REFUSED (same raise site).
- **#626 d8 / w2** (PRE-EXISTING false proofs) CLOSED: both now REFUSED (d8 by route #621 rule D, w2 by route #483
  on zv7w2/b.py's import-time writer). Also refused: the nested (`from pkg.sub import *`), relative (`from . import *`),
  computed `__all__`, extended `__all__` and outside-mutated `__all__` variants (n1 / n2 / n4 / n5 / n6). Controls
  n3 (literal `__all__`, benign submodule) and n7 (no `__all__`) still PROVE.
- **#627 z1** (PRE-EXISTING false proof) CLOSED: REFUSED, `PYCSL-SEM-IMPORT-PATH-NOT-DIRECTORY`.
- **Over-refusal measured BEFORE the narrowing (h1): root / pyref / mirror 0 MOVED / 0 GONE / 0 APPEARED. GONE list
  EMPTY.** Final (h2): the same, plus 5 new sources.
- src changes: `src/pycsl/frontend/ir_resolve.py` (only inside `resolve_imports`' u60 / #621 walk; `_inject_functions`
  untouched) and `src/pycsl/pycsl.py` (only inside `_run_pipeline`: its first lines (#627) and the #483 closure
  loop; nothing between `_BODY_EQ_RE` and `def main`). Mirror twins `resolve_imports` and `_run_pipeline` are
  `\trusted` (checked). No helper extracted, no new `\trusted` (366), no axiom (ledger 3), no gate edited (bin/
  change = 4 census rows), no mirror emission moves.

## 1. Rules (all inline)

**F. #627 (pycsl.py `_run_pipeline`, first check).** Every `--import-path` entry must be an existing directory
(`os.path.isdir`), else REFUSED (`PYCSL-SEM-IMPORT-PATH-NOT-DIRECTORY`, stage imports). pycsl only probes
directory roots, CPython's zipimport imports from a zip on sys.path. Not ignored by CPython, so refused in every
mode. Every `--import-path` in corpus `# pycsl-flags:` lines and in bin/ (mirror sweep, planes, gates) is a
directory (grep-checked; the mirror sweep is 0 diff).

**G. #626 (u60 walk in ir_resolve + #483 closure in pycsl.py).** A wildcard `from M import *` (any level, `M` may be
empty: `from . import *` resolves its anchor package's `__init__`) whose resolution (the program's view) is a
package `__init__.py` outside pycsl's `Lib/` is followed as `from M import <each __all__ name>`, i.e. those entries
are appended to the module's import entries and go through the same views / prefix rules / following as explicit
from-import targets (CPython's `_handle_fromlist` loads each `__all__` name the package does not bind). `__all__`
is read only when it is ONE top-level `__all__ = [...]` / `(...)` (or annotated) of identifier string literals and
the name `__all__` appears nowhere else in that `__init__` (no aug-assign, `.append`, `del`, import of it, `global`,
attribute / literal string "__all__"). No `__all__` at all = no submodule loaded (CPython loads nothing). Anything
else REFUSES with the new `PYCSL-SEM-IMPORT-WILDCARD-ALL-UNKNOWN` (walk) or route #483's existing site (closure,
same rule). Fail-closed extra: when a package wildcard is met and any reached module mentions `X.__all__` or the
string "__all__" (outside a package's own literal assignment), the walk refuses too (another module can change the
list: probe n6). The #483 closure applies the same expansion for both its anchors (dependency and program).

**H. Rule D (u69 o1 narrowing).** A wildcard import in the PROGRAM now counts like a non-program one (`"*"` added to
the import-name components), so an `__init__` `def b` candidate is refused whenever any reached module (program
included) has a wildcard. With G, d8's m.py is also reached and its `import zv7od8.b` refuses it on its own.

**E' (rule E narrowed, rt79 r1).** Per reached module, `_mc671` = every name an import statement binds (any scope).
A store / delete of attribute `n` (or literal-name `setattr` / `delattr`) whose receiver, rooted through
attribute / subscript / call / starred, is a Name in `_mc671` is judged as before. Any OTHER receiver is judged only
if some reached module lets a module object ESCAPE into a value (`_esc671`, fail-closed, global): a wildcard import;
an import inside a class body; an import-bound name (or attribute / subscript chain rooted at one) in any position
other than a call's callee, a store / delete receiver, an expression statement, `raise`, a decorator, a class base,
an `except` type (or tuple of them) or an annotation; a Load of `globals` / `vars` / `locals` / `eval` / `exec` /
`compile` / `__import__` / `__builtins__`; an attribute `modules`, `__dict__`, `__globals__`, `__builtins__`,
`__class__`, `_getframe`, `f_globals`, `f_locals`, `f_back`, `tb_frame`, `gi_frame`, `cr_frame`, `__self__`,
`__closure__`, `cell_contents`; an import of `importlib`, `inspect`, `pkgutil`, `runpy`, `pydoc`, `gc`, `ctypes`,
`builtins`, `__main__`, `pickle`, `marshal`, `copyreg`, `zipimport`, `imp`; or an absolute import that resolves to
no program file and is not a stdlib / builtin name (an installed library may return a module). The raise site and
its message are unchanged (census join of 10405 / 10406 preserved). Escape probes y2 (alias `q = pkg`), y3 (module
passed as an argument), y4 (import in a class body), y5 (function returning the module) all stay REFUSED; y6 (r1 plus
`f = three`) is refused by the fallback (fail-closed; also refused at b0 / b1 by an unrelated rule).

Docs: u71 text added next to u69's in `test-suite/annotations.md`, `docs/pycsl-static-semantics-reference.md`,
`docs/pycsl-translational-reference.md` (doc-coherency rc 0).

## 2. Probes (full proofs P: hoare, PYTHON_CPU_COUNT=2, timeout 3600, cwd = tree root; b0 = L19, b1 = u69, head = h2)

CPython: `L/cpython-all.txt` (`tools/cpy.sh`: /usr/bin/python3 and venv 3.14, -B, ulimit -v 2000000, cwd /tmp or the
probe's cwd, PYTHONPATH = the --import-path entries). The two interpreters agree on every probe except r4 (the venv
has an installed `lark`; pycsl REFUSES r4 on every tree). pycsl: `L/chain2.txt` `[J b0|b1|h2] [p]` lines, logs in
`L/J-{b0,b1,h2}/p/`. Full table of all 108 probes + witnesses + helpers: `L/J-table.txt` (name | CPython | b0 | b1 | head).

Every probe whose verdict differs between trees:

| probe | CPython | b0 (L19) | b1 (u69) | head |
|---|---|---|---|---|
| r1 (rt79) | 4 | SUCCESS | REFUSED (rule E) | **SUCCESS** (repair) |
| d8 (rt79) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (#621 rule D) |
| w2 / w2-dep (rt79) | 5 / b.py loaded | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (#483) |
| z1 (rt79) | 2 (zipimport) | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (PATH-NOT-DIRECTORY) |
| d9 (rt79) | TypeError | SUCCESS (partial corr.) | SUCCESS | REFUSED (rule D, fail-closed) |
| n1 (u71: computed `__all__`) / n1-dep | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (WILDCARD-ALL-UNKNOWN) |
| n2 (u71: `__all__.append`) | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (WILDCARD-ALL-UNKNOWN) |
| n4 (u71: `from . import *`) | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (#483) |
| n5 (u71: `from pkg.sub import *`) | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (#483) |
| r2 r3 r9 r2d r2r r2d-dep v2d w5 x2 r12c t4 t8 t11 t13 o2 o3 | 2 / TypeError | SUCCESS | REFUSED | REFUSED (= u69) |
| r12 | 2 | SUCCESS | FAIL | FAIL (= u69) |
| b21 / o4 | 1 / 2 | FAIL | REFUSED | REFUSED (= u69) |
| s1-dep / c1 | Q loaded / 1 | REFUSED | SUCCESS | SUCCESS (= u69) |
| s7-dep | ModuleNotFoundError | SUCCESS | REFUSED | REFUSED (= u69) |

Unchanged on all three trees (head = b1 = b0): n3 SUCCESS (3), n7 SUCCESS (4), n6 REFUSED (5; refused on every tree,
at head by the new `__all__` trigger), y2 / y4 / y5 REFUSED (2), y3 / y6 REFUSED, t12 / d7 REFUSED, and every other rt76 / rt78 / u64 /
u66 / u69 / rt79 probe (see `L/J-table.txt`). **No head SUCCESS where b1 refused except r1 / 10440 (CPython 4 = the
claim).** No head SUCCESS that CPython contradicts.

Process note: my first QUICK probe batch (`L/dev1`, ~01:15Z) overlapped my own base sweep for ~3 min (the sweep had
taken its slot at 01:12 while I believed it queued); every later job ran strictly one at a time.

## 3. Over-refusal (cwd = tree root, each compared once against base b1 = 73f47db9d)

| sweep | h1 (pre-narrowing, MEASURE) | h2 (final src) | logs |
|---|---|---|---|
| root | rc 0, 3334 / 3334: 0 MOVED / 0 GONE / 0 APPEARED | rc 0, 3334 / 3339: 0 / 0 / 0, 5 new sources | `L/G/C-h1-root.txt`, `L/G/C-h2-root.txt` |
| pyref | rc 0, 2185 / 2185: 0 / 0 / 0 | rc 0, same | `L/G/C-h{1,2}-pyref.txt` |
| mirror (53) | rc 0: 0 / 0 / 0, diff -rq 0 lines | same | `L/G/C-h{1,2}-mir.txt`, `L/G/D-h{1,2}-mir.txt` |

**GONE list: EMPTY** (h1 and h2). New sources on h2: 10439, 10440, zh35, zh36, zh37 (the FAIL witnesses and zd3x
helpers do not emit). Sweep logs: `L/chain1.txt`, `L/chain2.txt`, `L/G/S-base.txt`.

## 4. Witnesses (IDs 10435-10440 inside [10435, 10449]; CPython from the tree root, both interpreters)

| witness | CPython | b0 | b1 | head | header |
|---|---|---|---|---|---|
| 10435_r626x_dependency_wildcard_all_loads_writer_submodule_false (w2 shape) | 5 | SUCCESS (false) | SUCCESS (false) | REFUSED (#483) | FAIL |
| 10436_r626x_dependency_wildcard_of_subpackage_all_loads_writer_false (`from pkg.sub import *`) | 5 | SUCCESS (false) | SUCCESS (false) | REFUSED (#483) | FAIL |
| 10437_r626x_dependency_wildcard_of_computed_all_false (new site) | 5 | SUCCESS (false) | SUCCESS (false) | REFUSED (WILDCARD-ALL-UNKNOWN) | FAIL |
| 10438_r627x_zip_archive_on_import_path_false (zip in corpus, new site) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (PATH-NOT-DIRECTORY) | FAIL |
| 10439_r626o_program_wildcard_literal_all_benign_submodule_ctl | 3 | SUCCESS | SUCCESS | SUCCESS | PASS |
| 10440_r621o_unrelated_self_store_named_like_submodule_ctl (r1 shape) | 4 | SUCCESS | REFUSED | SUCCESS | PASS |

#627 is a corpus witness (not just a probe): the zip `multi_file_lib/u71z/lib.zip` (one benign `.py`, stored, fixed
timestamp; no bytecode) plus `multi_file_lib/u71y/zh38.py`. Helpers: `zh35/36/37.py`, `zd35/36/37.py`, `zp35/`,
`zp36/` (+`sub/`), `zp37/`, `zp39/`, `zp40/`. Helper own runs: zh*, zp*/`__init__`, zp39/k, zp40/* SUCCESS on all
trees; zd35/36/37 REFUSED at head (correct: their own run executes the wildcard that loads the writer); zp3x/b.py
REFUSED on every tree (pre-existing rebound-name rule; their own run does rebind). check-corpus-executes loads every
helper (rc 0). Census: real `_census_row` (`tools/CR.sh`) for 10435-10438, appended to
`bin/refusal-witness-census.tsv` (`L/CR-rows.tsv`; 10435 / 10436 rows carry the #483 message's absolute path, as
that message prints it). Rule 38: full IDs unique; the 4-character cut gains `1043` / `1044` duplicates (67 -> 69),
the same artefact u69 recorded for `1040`.

## 5. Gates (final src 08e65645c + census rows; `tools/chain2.sh` -> `tools/GATES.sh`, cwd = u71 tree, one NORMAL job)

| gate | result | log |
|---|---|---|
| byte-diff root / pyref vs b1 | rc 0 / rc 0, 0 MOVED, 0 GONE, 0 APPEARED | `L/G/C-h2-root.txt`, `L/G/C-h2-pyref.txt` |
| mirror sweep 53 + diff -rq | rc 0, 0 lines | `L/G/C-h2-mir.txt`, `L/G/D-h2-mir.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency --check (fidelity) | rc 0 / 0 / 0 | `L/GATES/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast + conversion tier, full tee) | rc 0, 62 / 62 green | `L/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 492 demonstrated (u69 490; +2 = the two new sites), 5 undemonstrated (ceiling 5) | `L/GATES/rwc.txt` |
| check-corpus-executes | rc 0 (only the known load failures) | `L/GATES/ce.txt` |
| frontend-only-conformance | rc 0: 38 OK / 0 MISMATCH | `L/GATES/foc.txt` |
| check-dropped-mutation | rc 0: 0 / 49 / 5 / 0 | `L/GATES/cdm.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `L/GATES/lg/mir_emit`, 53) | `L/GATES/lg/*.txt` |
| \trusted | 366 | `L/chain2.txt` [LG] |
| ledger | 3 (no allowlist / axiom change) | -- |

## 6. Commits (branch run9-u71, not pushed)

- f536b181f merge ghost-assign-bc6 (setup).
- e580aae79 WIP h1: #626 + #627 + rule D program wildcard; probes, tools; `git rm --cached progress.txt`.
- 08e65645c WIP h2: rule E narrowing, witnesses 10435-10440 + helpers, docs.
- 5a89806ad WIP: h1 compare logs.
- final: census rows, chain2 / gate logs, J table, this report.

## 7. Open / for the driver

- Rule E' trusts that a module object reaches a non-import name only through the listed escapes. Not covered: a
  module object produced by a stdlib function outside the deny-list (none known besides those listed) and an aliased
  `setattr` (`sa = setattr; sa(pkg, "b", c0)`) at RUN time in a function the program calls (u69 had the same gap;
  import-time forms are refused by #483). Worth a red-team pass.
- G reads `__all__` statically; a package whose `__init__` gets `__all__` via a wildcard of another module is caught
  only by the global "__all__" string trigger (the other module's literal list holds "__all__") or by route #621.
- d9 (CPython TypeError, no false claim) is now refused by rule D's program-wildcard count: fail-closed cost.
