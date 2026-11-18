# OPEN ROUTE #613: a module CPython loads TRANSITIVELY can be a local file the program never imports

**Status: REPAIRED (refusal-only)** on run #8, branch run8-u52, by executor u52. USER DECISION of
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

## Declared run mode `--as-package-module ROOT` (driver decision)

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
