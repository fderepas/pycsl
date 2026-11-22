# run #9 executor u64: route #613 V2D (review rt74), refusal-only, import resolver

Branch `run9-u64`, tree `/home/fabrice/git/pycsl-u64`, base `run9-u63` 2f93b9c56, with run9-u63's
2873a902d merged in on the driver's note (merge 0a0add9aa) BEFORE any gate. Every base measurement
uses the detached tree `/home/fabrice/git/pycsl-u64-base` at 2873a902d. Brief
`scratchpad/run9/brief-u64.md`. Logs under `scratchpad/u64/logs/` (written `L/` below), tools in
`scratchpad/u64/tools/`, probes in `scratchpad/u64/probes/`. All committed except the bulky sweep
emissions (`L/G/{base,head}/{bd,mir}`, `L/G/lg/mir_emit`, `L/q-*/`, which stay on disk).
oom_kill was 15 at the start and end of every job. No result is VOID.

## 0. Status

- V2D rule ported and GATED. All gates green on 427045b14 (the src / corpus / census state; later
  commits add only logs and this report).
- Witness redesign: one file added to u61's shape (`zpy61_alt/__init__.py`). The corpus witnesses
  now load under `check-corpus-executes` (rc 0), still PROVE a false claim on the base tree (or
  prove where CPython raises), and are REFUSED at head.
- v1f (rt74 / u61 method-call mutation): the program PROVES its false claim at base AND at head.
  This is not fixed here and is reported as the next item (section 4).
- V1D stays OPEN, as in u61's e41e561ad.
- No new `\trusted` (366), no axiom (`proof_axiom_allowlist.py` untouched, ledger 3), no gate
  loosened, no tooling edit. The only `bin/` change is 3 data rows in
  `bin/refusal-witness-census.tsv`. No mirror emission moves.

## 1. The rule (u61 e41e561ad, V2D only)

`src/pycsl/frontend/ir_resolve.py::resolve_imports`, inline in u60's DEPENDENCY-SEARCH-ORDER block
(no helper). I checked with grep before editing: the mirror twin
`src/self-annotate/src/frontend/ir_resolve.py::resolve_imports` is `\trusted`. u61's diff
`f5adbfd1f..e41e561ad` for ir_resolve.py and the three docs (`test-suite/annotations.md`,
`docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md`) applied with
`git apply` and no conflict, because those four files are byte-identical between f5adbfd1f and
run9-u63. The rule runs in script mode only and is skipped under `--verification-image`.

1. Every import of every reached module is expanded into all of its dotted prefixes `a`, `a.b`, ...,
   shortest first. Each prefix is compared between the module's own view and the program's view at
   u60's existing raise site, and is then followed.
2. A new raise site, code `PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER`, works in the program's order.
   Each prefix that resolves to a file must be a package `__init__.py` whose directory holds the
   file pycsl reads for the full name. The import is REFUSED if a prefix resolves to a module file,
   to another package's `__init__`, or to a refused resolution. pycsl's own `Lib/` model root is
   exempt.

Commit 10c4ea95e.

## 2. Probes, base (2873a902d) vs head: which file does CPython actually load?

The `--no-proof` runs used cwd = tree root (`L/q-base.txt`, `L/q-head.txt`;
`HEAVY_QUICK=1 heavy.sh bash scratchpad/u64/tools/qb.sh <tree> <out>`). The CPython runs used both
`/usr/bin/python3` and the venv 3.14, with `-B`, `ulimit -v 2000000`, cwd /tmp
(`L/cpython-probes.txt`, `tools/cpyall.sh`).

u61's own probe directory no longer exists: the u61 worktree is gone and its scratchpad was never
committed. I rebuilt x1, x2, x3, v2down and v1f in `scratchpad/u64/probes/` from u61's report.
v2d, w5 and v2 are copies of rt74's.

| probe | what CPython loads (both interpreters) | base | head (u64) |
|---|---|---|---|
| v2d (dep `from zpa74.b import one`, P/zpa74 redirects `__path__`) | P/zpa74_alt/b.py, "result 2" | SUCCESS | REFUSED (prefix `zpa74` compared, u60 site) |
| w5 (`import zpa74.b`) | P/zpa74_alt/b.py, "result 2" | SUCCESS | REFUSED (prefix, u60 site) |
| v2 (program imports `zpa74.b` itself) | P/zpa74_alt/b.py, "result 2" | REFUSED (#483, `__path__` at import time) | REFUSED (new prefix site, earlier stage) |
| x1 (dependency in the program dir) | P/zpa74_alt/b.py, "result 2" | REFUSED (#483) | REFUSED (new prefix site) |
| x2 (program, empty regular P/zpb74, b only in X) | ModuleNotFoundError `zpb74.b` | SUCCESS | REFUSED (new prefix site) |
| x3 control (zpa74 only in X2) | X2/zpa74/b.py, "result 1" | SUCCESS | SUCCESS |
| v2down (X2/depv2.py as its own script) | X2/zpa74/b.py (`one()` = 1; checked with sys.path[0] = X2) | SUCCESS | SUCCESS |
| v1f (see section 4) | "result 2" | SUCCESS | SUCCESS |

This is the same as u61's section 1 table. Every refusal is on a case where CPython runs a file pycsl
did not verify, or raises. Both controls still pass.

## 3. Witness redesign (corpus IDs 10340-10344 used, inside [10340, 10359])

**Why u61's version failed.** `bin/check-corpus-executes.py` loads every PASS-expected corpus `.py`,
recursively, and skips files whose text contains `# pycsl-expected: FAIL`. A file inside a
directory below the corpus root is imported by its dotted name, with
`importlib.import_module("<dotted path>")`, cwd = the corpus root. So the corpus-root package file
`zpy61/__init__.py` is imported as `zpy61.__init__`. CPython first runs `zpy61/__init__.py`. That
file redirects `__path__` to `zpy61_alt/`, and the submodule `__init__` is then looked up there.
u61 had no `zpy61_alt/__init__.py`, so the load failed with "No module named 'zpy61.__init__'".
The other 8 non-loading files in u61's G1 run were the 8 KNOWN_LOAD_FAILURES (circ_b + 7 x1_h466*),
which I reproduced here.

**The new shape.** u61's files are restored as they were, plus `zpy61_alt/__init__.py`, a
comment-only file. That makes `zpy61_alt/` a regular package, so `zpy61.__init__` resolves to it
and loads.
- The witnesses' own behaviour does not change. `zpy61.b` is still loaded from `zpy61_alt/b.py`,
  which prints "result 2". CPython never runs `zpy61_alt/__init__.py` for that import.
- Before any sweep I checked each of the 14 helper modules with real CPython under the plane's
  exact load mode (`import_module`, cwd = corpus root). Every one loads.
- Witness files: `10340_r613y_dependency_dotted_prefix_package_false.py` (FAIL),
  `10341_r613y_dotted_import_prefix_regular_package_elsewhere.py` (FAIL),
  `10343_r613y_dependency_dotted_module_import_prefix_false.py` (FAIL),
  `10344_r613y_dependency_relative_dotted_import_ctl.py` (PASS control).
- Helper files: `zpy61/__init__.py`, `zpy61_alt/{__init__,b}.py`, `zpy62/__init__.py` (corpus
  root); `multi_file_lib/r613y/X2/{r613y_depv2,r613y_depw5,zpy61/__init__,zpy61/b}.py`,
  `X3/zpy62/{__init__,b}.py`, `lib4/{__init__,dep4,zpq61/__init__,zpq61/b}.py`. There is no file
  overlap with u58's existing `r613y/{g5,g6,g7,nsctl.py}`.

| witness | CPython (`L/cpython-witnesses.txt`) | base full proof | head full proof | header |
|---|---|---|---|---|
| 10340 (dep `from zpy61.b`) | zpy61_alt/b.py, "result 2" | SUCCESS (false `== 1`) | REFUSED (prefix `zpy61`, u60 site) | FAIL |
| 10341 (program `from zpy62.b`) | ModuleNotFoundError `zpy62.b` | SUCCESS | REFUSED (new prefix site) | FAIL |
| 10343 (dep `import zpy61.b`) | zpy61_alt/b.py, "result 2" | SUCCESS (false `== 1`) | REFUSED (prefix, u60 site) | FAIL |
| 10344 control (package-relative) | "result 1" | SUCCESS | SUCCESS | PASS |

The full proofs use hoare and PYTHON_CPU_COUNT=2; `L/J.txt`, logs in `L/J/pr-{base,head}/`. Each
verdict at head equals the file's `# pycsl-expected:` header. These were re-run at the final src
state in `L/CR.txt`. The base runs used the base tree's pycsl with cwd = the u64 tree root,
because the witness files exist only there.

Census rows (commit 427045b14): I first ran `--append-new`. It would have run all 505 FAIL witnesses
that have no row at base (a pre-existing backlog, almost none of them mine). I killed it before it
wrote anything (own PIDs; parent chain checked; `L/G/census-append.txt` is empty; the tsv was
unchanged). I then wrote the 3 rows with `_census_row`'s exact parse applied to the head pipeline
output. CR.sh re-ran the real `_census_row` on the 3 files and compared the result with the
committed rows (`L/CR/`, `L/CR.txt`).

The new prefix site is DEMONSTRATED: rwc reports 488 demonstrated and 5 undemonstrated, against a
ceiling of 5. 10341 fires it; 10340 and 10343 fire u60's site through the prefix compare.

## 4. v1f: method-call mutation of a dependency global (MEASURED; not fixed, for the driver)

The probe is `scratchpad/u64/probes/v1f/P/`:
- `prog.py` does `from dep75 import f` and declares `g` with `ensures \result == 1`;
- `dep75.py` does `from zqf75 import one`, sets `L = [1]`, and declares `f` with
  `ensures \result == 1`, `one(); return len(L)`;
- `zqf75.py` does `import dep75` and defines `one`, which does `dep75.L.append(7)` and returns 0.

CPython prints "result 2" with both interpreters.

| run (full proof, hoare, PYTHON_CPU_COUNT=2) | base 2873a902d | head |
|---|---|---|
| `pycsl.py P/prog.py` | **PROVES** (SUCCESS) | **PROVES** (SUCCESS) |
| `pycsl.py --deep P/prog.py` | **PROVES** | **PROVES** |
| `pycsl.py P/dep75.py` (the dependency's own run) | REFUSED (#483: zqf75 "imports the claimed file itself") | REFUSED (same) |

Logs: `L/J/pr-{base,head}/prog.log`, `L/J2/{base,head}-{dep75,prog-deep}.log`.
- The program's proof takes `f`'s contract as a trusted stub. The only run that could have
  established that contract is dep75's own run, and that run is refused. pycsl therefore PROVES
  `g`'s false claim while the premise it relies on is never verified.
- Under `--deep`, pycsl reports "Circular import detected: dep75 -- skipping" and imports
  `L.append` / `one` as trusted stubs. It still proves.

This gap is pre-existing and independent of V2D. My reading of a direction, which I have not
implemented: apply the route #483 closure rules (they refuse dep75's own run) to every module the
program reaches, not only to the claimed file. Equivalently, refuse an import whose module's own
run is refused.

## 5. Gates (final src state 427045b14; job `L/ALL.txt`, `heavy.sh bash scratchpad/u64/tools/ALL.sh`, NORMAL)

| gate | result | log |
|---|---|---|
| byte-diff root, base 2873a902d vs head (cwd = each tree root) | rc 0: 3325 / 3326 .mlw, 0 MOVED, 0 GONE, 0 APPEARED, 1 new source (10344) | `L/G/C-root.txt` |
| byte-diff pyref | rc 0: 2185 / 2185, 0 / 0 / 0 | `L/G/C-pyref.txt` |
| mirror sweep (53 files) | compare rc 0, 53 / 53, 0 / 0 / 0; `diff -rq` 0 lines | `L/G/C-mir.txt`, `L/G/D-mir.txt` |
| check-self-annotate-sync.sh | rc 0 | `L/G/lg/sync.txt` |
| self-annotate-mirror-check.sh | rc 0 | `L/G/lg/mircheck.txt` |
| doc-coherency.py --check | rc 0 | `L/G/lg/doccoh.txt` |
| run-soundness-planes.sh (fast) | rc 0, 62 / 62 ok | `L/G/planes.txt` (full) |
| check-refusal-witness-coverage | rc 0 (488 demonstrated, 5 undemonstrated, ceiling 5) | `L/G/rwc.txt` |
| check-corpus-executes | rc 0: 2621 / 2629 load, the 8 failures are all KNOWN; 1703 / 1703 self-checks pass | `L/G/ce.txt` |
| check-assigns-writes-survival | rc 0 | `L/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 | `L/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 | `L/G/lg/check-getattr-erasure.txt` |
| `\trusted` count | 366 (unchanged) | `L/ALL.txt` |
| ledger | 3: `proof_axiom_allowlist.py` not edited, no axiom added | -- |
| new corpus files: full verdict == header | 4 / 4 | `L/J.txt`, `L/CR.txt` |

The two ledger planes that take an emission ran on a head mirror emission written with the planes'
single-underscore naming (`L/G/lg/mir_emit`, `tools/LG.sh`).

Duplicate IDs (rule 38). `ls test-suite/corpus/pycsl-reference | cut -c1-4 | sort | uniq -d` is
already NOT empty at base: 60 lines, from the `NNNN.py` / `NNNN.proofs` pairs, `1033` (10330-10332
against `1033_route39_*`) and `r613`. At head it gains exactly two lines:
- `1034`: the 4-character cut of the 5-digit 10340-10344 matches `1034_route39_*`. This is the same
  pattern as the base's `1033`, not a real ID clash.
- `zpy6`: the helper directories `zpy61/`, `zpy61_alt/` and `zpy62/`, which are not IDs.

With the full numeric ID (`ls *.py | sed 's/_.*//' | sort | uniq -d`), base and head give the same
output: only `r613z`, which is pre-existing and not an ID. **The rule's literal check therefore
reports 2 more lines at head than at base, both artefacts of the 4-character cut; the driver
should decide whether that is acceptable.**

## 6. Commits (branch run9-u64, not pushed)

- 10c4ea95e: V2D port, rule + docs
- 0a0add9aa: merge run9-u63 (2873a902d), at the driver's request
- 83752df95: WIP, witnesses (+ `zpy61_alt/__init__.py`), probes, tools, CPython logs
- 5f12811e9: WIP, witness and v1f proof logs, gate scripts
- 427045b14: census rows 10340 / 10341 / 10343
- the report commit (this file + gate logs)
