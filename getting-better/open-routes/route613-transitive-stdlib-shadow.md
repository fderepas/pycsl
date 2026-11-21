# OPEN ROUTE #613: a module CPython loads TRANSITIVELY can be a local file the program never imports

**Status: REPAIRED (refusal-only)** on run #8, branch run8-u52, by executor u52; FOLLOW-UP REPAIR
of review rt66's five gaps (g01 / g02 / g08 / g09 / g10) on branch run8-u55 by executor u55 (see the
section "u55 follow-up" at the end, and `getting-better/run8-u55-report.md`); ROUND 3 on branch
run8-u58 by executor u58 after review rt69 (section "u58 round 3" at the end,
`getting-better/run8-u58-report.md`): `--as-package-module` WITHDRAWN (rc 2), and the
pre-existing gaps G5 / G6 / G7 closed; ROUND 4 on branch run8-u60 by executor u60 after review rt72
(section "u60 round 4" at the end, `getting-better/run8-u60-report.md`): A1 (a dependency's absolute
imports) closed, O1 (u58's G6 over-refusal) measured and NOT narrowed. USER DECISION of
2026-11-18: "really bad, recursively check imported modules". Recorded first as u50's residual (log
1071), then opened as a route (log 1090).

## Defect (PRE-EXISTING: measured at 899b6869d and at 0057c8b94)

CPython puts the realpath of the script's directory first on `sys.path`, so an import made INSIDE an
imported module resolves there first too. Routes #326 / #611 / r12 judged only the modules named by the
program's own import statements. Measured with real CPython 3.14.4 (`witnesses-r613/cpython.txt`, both
`/usr/bin/python3` and the venv interpreter):

- `import json` with a local `re.py`: `json`'s `import re` loads the local file.
- `import hashlib` with a local `_hashlib.py`: the OpenSSL extension lives in lib-dynload, AFTER the
  script directory, so the local file wins.
- NO import statement, and `"a".encode("idna")` with a local `re.py`: the codec registry imports
  `encodings.idna`, which imports `re`.

pycsl admitted all three and PROVED their contracts: hoare at both bases, and the hashlib one in all
three memory models (`witnesses-r613/jobA/base-*`, `pr-*`).

## Rule (`resolve_imports`, top-level call only; mirror twin `\trusted` with `raises` declared)

Code `PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW`. The import closure can never be computed exactly. The
builtins' C code imports modules that no source shows: codec lookup, `warnings`, `locale`, an uncaught
exception's `traceback` / `linecache`. Hence the CONSERVATIVE rule applies to EVERY program, including
one with no import statement.

**What is judged.** Every entry in ANY resolution root whose top-level name the closure may reach. The
roots are the realpath of the program's directory, its directory, cwd, `src/`, `Lib/` and each
`--import-path`. The names are:

- the names in `sys.stdlib_module_names` and `sys.builtin_module_names`;
- every top-level name the interpreter's own stdlib source imports, anywhere in that source. This adds
  `sitecustomize`, `usercustomize`, `setuptools`, `pip`, `java`, `_testcapi`, and so on.

Each such entry is judged exactly as if the program imported that name directly: `_resolve_module_path`
applies the #326 / #611 / r12 rules.

**What survives.** Only two kinds of entry:

1. A byte-identical stdlib copy that passes #326, #611 and r12. CPython then runs the same source and
   bytecode it would take from `Lib/`.
2. A bare namespace directory that a builtin, frozen or regular stdlib module of that name outranks.

Everything else is refused, including a non-stdlib local module the stdlib imports (such as
`sitecustomize.py`).

**The chain in the message.** The message names a chain found by a breadth-first walk from the
program's imports, through the local modules they name, over the stdlib import graph. Examples are
`program -> json -> re -> …/re.py`, and `program -> builtins (C code …) -> re` when no import statement
reaches the name.

## Declared run mode `--as-package-module ROOT` (driver decision; WITHDRAWN by u58, see the end)

The program is declared to be imported as a submodule of the package rooted at ROOT, never run as a
script.

- ROOT (and its realpath) takes the place of the program's directory, but only among THIS check's
  roots. The program's own imports resolve exactly as before, so the emission is identical.
- The mode is opt-in and never inferred. It is parsed in `main()` and passed to pycsl's sub-invocations
  as `PYCSL_AS_PACKAGE_MODULE`.
- `--soundness-report` lists it as the model assumption AS-PACKAGE-MODULE.
- `main()` refuses a ROOT that does not contain the file (rc 2).

The mirror gates pass ROOT = `src/self-annotate/src`, the mirror's image of `src/pycsl` (where the
entry script `pycsl.py` makes `sys.path[0]`). This applies to `bin/mirror-emit-sweep.sh`, the shared
mirror emission of `bin/run-soundness-planes.sh`, and every mirror-emitting check.

Why the mode is needed: in script mode the 16 files of `module6_whyml/` are refused, because their
sibling `types.py` shadows the stdlib `types` (`typing` -> `types`). That refusal is CPython-faithful.
With the venv interpreter and that directory as `sys.path[0]`, `import typing` loads the local
`types.py` and fails with a circular-import error.

## The stdlib table and its cache

The table is cached at `src/pycsl/__pycache__/r613-stdlib-imports-<key40>.json`. Each entry maps a
top-level stdlib name to every top-level name imported by any `.py` of that module or package.

- **Key.** sha256 over `"r613-v1"`, `sys.version`, `cache_tag`, the stdlib path, both name sets, and
  (relpath, size, mtime_ns) of every stdlib `.py`, re-walked on every run.
- **Use.** The table is used only when its stored key equals the computed key and its shape is
  `{str: [str]}`. Otherwise it is rebuilt and atomically replaced: when it is absent, unreadable,
  truncated, malformed or stale.
- **Name.** A `.json` file name never matches the r12 cache scan (`<m>.<cache_tag>[.opt-N].pyc`), and
  the #611 walk skips `__pycache__`.
- **Evidence.** `witnesses-r613/cache-test.*`.
- **Cost.** About 2.6 s, once per interpreter. A warm run is unchanged: 1.31 s per `--no-proof` run at
  base and at HEAD, over 5 runs.

## Witnesses (corpus 10180-10188; `multi_file_lib/r613/`)

| file | layout | expected |
|---|---|---|
| 10180 | json + `re.py` | FAIL |
| 10181 | hashlib + `_hashlib.py` | FAIL |
| 10182 | no import + `re.py` | FAIL |
| 10183 | json + `sitecustomize.py` | FAIL |
| 10184 | json + sourceless `re.pyc` | FAIL |
| 10185 | local dependency -> json + `re.py` | FAIL |
| 10186 | json + bare `re/` | PASS control |
| 10187 | json + identical `codecs.py` | PASS control |
| 10188 | json, no shadow | PASS control |

## Residuals

- **Time of check vs time of use.** A shadow file, or a forged table, created after verification.
- **A writable pycsl install directory.** Someone who can write `src/pycsl/__pycache__` can forge a
  well-formed table carrying the right key, for example one with an empty graph. That would drop the
  non-stdlib names from the check, such as `sitecustomize`. The stdlib names always come from
  `sys.stdlib_module_names` itself. This is the same trust as pycsl's own source in that directory.
- **The program's runtime environment.** The user's PYTHONPATH, `.pth` files, user site-packages, a
  different interpreter whose stdlib or startup set differs, a case-insensitive file system.
- **Dynamic imports of program-chosen names**, for example `pickle.loads` naming a local module, or
  `importlib` with a program-provided string. The second case is covered by #326 only when a local
  import is also present.
- **Over-refusals (fail-closed, documented).**
  - The import table is top-level and flow-insensitive, so a name imported only in a dead branch still
    counts, such as `java` in `platform`.
  - A script-directory `sitecustomize.py` is refused, although CPython's `site` runs before
    `sys.path[0]` exists. It IS loaded from a PYTHONPATH root.
  - A shadow of a startup-loaded module (`os`, `codecs`) is refused, although it is never re-imported.
    The startup set depends on the environment (Ubuntu's sitecustomize loads `types`; the venv's does
    not).


## u55 follow-up (review rt66: five closure gaps, all refusal-only)

Review rt66 (`scratchpad/rt66/FINDINGS.txt`) found five layouts where CPython loads a module pycsl
never analysed and pycsl still PROVED the program. Each is now refused; `getting-better/run8-u55-report.md`
has the base / head evidence.

| gap | origin | rule (code) |
|---|---|---|
| g02 | the declared mode | under `--as-package-module ROOT` every absolute import (program and dependencies) is resolved again with ROOT first; another file, or a file on one side only, refuses (`PYCSL-SEM-IMPORT-PACKAGE-MODE-ORDER`) |
| g08 | the declared mode | each parent package between ROOT and the program, and the program itself, must resolve from ROOT to its own `__init__.py` / file (#326 / #611 / r12 incl. the `__pycache__` / #475 judge each); each parent `__init__.py` is judged as a dependency: the import-system rule, and no dynamic import machinery (`PYCSL-SEM-IMPORT-PACKAGE-MODE-PARENT`, or the dependency's own `STATE-MANIPULATED`) |
| g01 | pre-existing | the judged names also hold every table key and every module entry of Lib / lib-dynload / the platform stdlib (computed names: `_sysconfigdata_*`), and literal names handed to `__import__` / `import_module` / `resources.files` (`tzdata`, `comtypes`); table key bumped to `r613-v2` |
| g10 | pre-existing | every candidate is judged IN ITS OWN ROOT (a notional entry script there), not only the first hit in pycsl's order |
| g09 | pre-existing, environment | the startup-hook closure: `sitecustomize` / `usercustomize` and `.pth` import lines in the site directories of the running interpreter AND its base installation, followed module by module (dotted names to `__init__` chains and module files; never into the stdlib); its own cache `r613-startup-hooks-<key40>.json`, valid only while every probed path keeps its (size, mtime) and every site directory its listing |

**New declared mode `--verification-image ROOT` (driver decision, USER-VISIBLE).** The mirror gates
no longer use `--as-package-module`. A faithful g02 cannot hold for the mirror. Its ROOT-level files
resolve `errors` / `frontend.*` to the MIRROR copies, while its subpackage files resolve the same
names, through `--import-path src/pycsl`, to the LIVE copies, and every such pair differs. So no
single `sys.path[0]` makes both groups resolve as CPython would.

- Meaning: the file is a verification model that CPython never executes. It makes NO claim about
  a CPython run.
- Its own imports resolve as pycsl resolves them, and only the closure check's roots move to ROOT.
  #613 / #611 / r12 / g01 / g09 / g10 all still apply.
- Listed by `--soundness-report` as VERIFICATION-IMAGE. Never inferred, and it excludes
  `--as-package-module`.

**`check-stdlib-modules-verify` declares `--as-package-module src`.** It was red at int69: its
`src/pycsl_lib/__init__.py` was refused, because that directory holds stdlib-named model packages.
The library is imported as `pycsl_lib.X` (pyproject `packages.find where = ["src"]`, through the
editable install's `.pth`), which is the faithful user-facing mode.

**Residuals (u55).**

- **Environment.** The startup-hook closure reads the site directories that pycsl's interpreter
  and its base installation have now. A different interpreter, PYTHONPATH- or `.pth`-added
  directories that hold a `sitecustomize`, and user site directories that are disabled at
  verification time but enabled at run time remain residual.
- **Flow-insensitive hooks.** The hook closure follows every import of each reached module,
  including dead branches (`_distutils_hack` -> `setuptools`, ...).
- **Over-refusal.** A `test/` package or `test.py` beside a program stays refused. `test` is a
  stdlib directory, and g01 requires every such name. Over-refusal numbers are in the report.


## u58 round 3 (review rt69: G1-G7; refusal-only)

Review rt69 (`scratchpad/rt69/FINDINGS.txt`) found seven layouts where pycsl PROVED a program whose
CPython run executes code pycsl never read. Report: `getting-better/run8-u58-report.md`.

| gap | origin | resolution |
|---|---|---|
| G1 shallow parent `__init__` check, G2 `python -m pkg` with an unread `__main__.py`, G4 ancestor namespace portion vs site-packages; over-refusals o06 / o07 | `--as-package-module` | the mode is WITHDRAWN: the flag (both spellings) exits rc 2 before anything is verified; its code paths (PACKAGE-MODE-ORDER, PACKAGE-MODE-PARENT), docs and soundness-report entry are removed; an inherited `PYCSL_AS_PACKAGE_MODULE` is ignored |
| G3 rule skipped for a program FILE named `__pycsl_r613_entry__.py` | the g02 rule | removed with the mode; no rule tests a file name (a script of that name is judged like any other) |
| G5 local namespace portion vs a regular installed package | pre-existing | `PYCSL-SEM-IMPORT-NAMESPACE-PORTION-SHADOWED`: a dotted import through a top-level directory without `__init__.py` refuses when another CPython root (program dir, `--import-path`, stdlib, site dirs, `.pth` dirs) holds that name |
| G6 a third-party package's own imports load local files | pre-existing | the closure's judged names add every top-level name importable from the site dirs and every name their sources import (cache `r613-site-imports-<key40>.json`); not judged in a cwd that is no CPython root |
| G7 pycsl's cwd as a resolution root | pre-existing | `PYCSL-SEM-IMPORT-CWD-ROOT`: a module found first in the cwd refuses, unless the cwd is the program dir / an `--import-path` root, or the module is an admitted byte-identical stdlib copy (`./json/`) |

`--verification-image ROOT` stays (mirror gates); `check-stdlib-modules-verify` now declares it
(`--verification-image src`) instead of the withdrawn mode. A declared mode is never enabled by an
inherited environment variable: `PYCSL_VERIFICATION_IMAGE` counts only with the token of an
ancestor pycsl process whose own command line carries the flag.

Over-refusal before the one narrowing (G6 names in a non-CPython cwd): every corpus (3299), pyref
(2185) and mirror (53) emission GONE, all through the repo root's bare `foobar/` directory. After:
0 MOVED / 0 GONE / 0 APPEARED in all three. Witnesses 10300-10307 (`multi_file_lib/r613y/`).

Residuals (u58): flow-insensitive site-source names; the site table is pycsl's interpreter's;
`src/` / `Lib/` model roots are exempt from G7 by design; PYTHONPATH containing the cwd; the
`/proc`-based token (fail-closed without `/proc`); #612 d19 auto-frame (`self.n = old self.n` over
an incrementing `__call__`, fails, recorded only).


## u60 round 4 (review rt72: A1 and O1; refusal-only)

Review rt72 (`scratchpad/rt72/FINDINGS.txt`) found one gap (A1, PRE-EXISTING, a false claim PROVED at
the u58 head and at 899b6869d) and one over-refusal introduced by u58's G6 (O1). Report:
`getting-better/run8-u60-report.md`.

| item | origin | resolution |
|---|---|---|
| A1 a local dependency's absolute imports resolved from the DEPENDENCY's directory (CPython: the program's `sys.path`) | pre-existing | `PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER` (`resolve_imports`, top-level call, script mode only): every local module the program reaches (transitively, package `__init__` chains included, every import statement) has each absolute import resolved from its own directory and through the program's order; refused when the own-directory view is a file (or pycsl's model of a stdlib name) and the program's view differs. A non-stdlib name with no module from the dependency's directory was an unconstrained `val` there and is admitted. Relative imports are only followed. Skipped under `--verification-image` |
| O1 ~370 site-only names judged for every program (`validate`, `checks`, `testing`, `path`, `parent` refused beside a program that imports no third-party code) | u58 G6 | NOT narrowed: no sound narrowing exists on this host. The builtins' C imports are unbounded below "all stdlib", and from the stdlib (top-level table, and even a module-level graph with `__main__` blocks pruned) the closure always reaches `pip` (`ensurepip`) and `setuptools` (`test.support` <- `multiprocessing.util`), whose entry-point / computed imports can load any installed distribution |

Measured over-refusal of A1 (snapshot 0f0868f35, before the witnesses): corpus root 3309 / 3309, pyref
2185 / 2185, mirror 53 / 53 emitted, byte-identical to int73 (0 MOVED / 0 GONE / 0 APPEARED). Witnesses
10330 / 10331 (FAIL, `multi_file_lib/r613z/`, corpus-root helpers `r613z_one.py` / `r613z_two.py`), 10332
(PASS control, package-relative import).

Residuals (u60): A1 compares pycsl's two resolutions, so pycsl's model roots (`src/`, `Lib/`, the cwd)
sit in both views between the program's directory and `--import-path`, unlike CPython (u58's G7
residual); a dependency imported only through a computed name is not followed; the PYTHONPATH /
interpreter environment residuals stand. O1's over-refusal stands as documented by u58 (a local module
named like any of ~370 installed / imported names is refused).
