# run #8 executor u52: route #613, transitive stdlib shadowing (SOUNDNESS BATCH S3, refusal-only)

Branch `run8-u52`, tree `/home/fabrice/git/pycsl-u52`, base `899b6869d` (L15). Brief
`scratchpad/run8/brief-u52.md`. Route file: `getting-better/open-routes/route613-transitive-stdlib-shadow.md`.

## 0. Status

- DONE. The rule is gated on snapshot `pycsl-u52-g3` @ f050b4ebb (jobB).
- Two later commits, 8b0140d61 and cb7f2516c, change only the route doc, the test scripts and two mirror
  tools. They were re-checked by jobC (§6).
- `\trusted` is 367 (unchanged). The proof-axiom ledger is 3 (`proof_axiom_allowlist.py` untouched).
- No new `\trusted`, no axiom, no gate loosened.
- oom_kill went 0 -> 5 between jobA and jobB. jobB itself ran entirely at 5 (start = end), so the rise
  came from someone else's job and voids none of my results.

## 1. Which file CPython loads (task 1; `witnesses-r613/cpython.txt`, `cpy.sh`)

Benign stand-ins. Each only defines what its importer touches and prints a marker. The runs used real
CPython 3.14.4 (`/usr/bin/python3` and the venv), under ulimit.

| probe | layout | CPython loads |
|---|---|---|
| j0 / h0 | `import json` / `import hashlib`, nothing beside | stdlib `re/__init__.py` / lib-dynload `_hashlib…so` |
| j1 | `import json` + local `re.py` | `witnesses-r613/j1/re.py` (MARKER local) |
| h1 | `import hashlib` + local `_hashlib.py` | `witnesses-r613/h1/_hashlib.py` |
| n1 | NO import statement, `"a".encode("idna")` + local `re.py` | the local `re.py` (via `encodings.idna`) |
| s1 | `import json` + `sitecustomize.py` in the script dir | not loaded; loaded when the dir is on PYTHONPATH (10183) |
| module6_whyml | `import typing` with that dir as sys.path[0] | venv: the local `types.py` (circular ImportError); system python: stdlib `types` (startup-loaded) |

## 2. pycsl verdicts at base (full proofs, x3; `witnesses-r613/pr-*/`, `jobA/base-*/`)

The verdicts are IDENTICAL at 899b6869d and at 0057c8b94, so this is PRE-EXISTING. It comes from
#326's design: only the program's own imports were judged.

| file | hoare | typed | store |
|---|---|---|---|
| j1, n1, 10180, 10182-10185 | PROVED | VERIFY-FAIL | VERIFY-FAIL |
| h1, 10181 | PROVED | PROVED | PROVED |

- **Typed / store VERIFY-FAIL.** These failures are unrelated to the route. The same bodies fail the
  same way with no shadow present (j0, 10188).
- **HEAD f050b4ebb.** j1, h1, n1, s1 and 10180-10185 are REFUSED in all three models. The controls
  j0, h0, 10186, 10187 and 10188 give the same verdicts as at base (`jobA/head/`).

## 3. The rule

The check lives in `resolve_imports`, top-level call only. Its mirror twin is `\trusted` and already
declares `raises`. The code is inline, with no helper. New code `PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW`.

**Always the conservative rule.** The closure always contains the builtins. Their C code imports
modules that no source shows: codec lookup, warnings, locale, traceback / linecache. So the closure is
never exact, and the brief's conservative rule applies to every program, with or without import
statements.

**What is judged.** Every entry in every resolution root whose name is in any of:

- `sys.stdlib_module_names`;
- `sys.builtin_module_names`;
- the top-level names imported ANYWHERE in the interpreter's stdlib source. These are function bodies,
  try / except fallbacks and `TYPE_CHECKING` blocks. They add, for example, `sitecustomize`,
  `usercustomize`, `setuptools`, `pip`, `java` and `_testcapi`.

The roots are the realpath of the program dir, the program dir, cwd, `src/`, `Lib/` and
`--import-path`. Entries include `.py` files, packages, bare directories and non-source artifacts.

Each entry is judged by `_resolve_module_path(name)`, which means the existing #326 / #611 / r12 rules
applied at that node. The original code is quoted in the message.

**What survives.**

- An admitted byte-identical stdlib copy (#326 + #611 + r12). CPython runs the same source and bytecode
  it would take from `Lib/`.
- A bare namespace directory that a builtin, frozen or regular stdlib module of that name outranks.

**Also refused.** A NON-stdlib local module that the stdlib imports, such as `sitecustomize.py`.

**Message.** It names a BFS chain over the stdlib import graph. Examples:
`program -> json -> re -> …/re.py`, `program -> r613_helper -> json -> re`, and
`program -> builtins (C code whose imports pycsl cannot see) -> re`.

**Declared run mode `--as-package-module ROOT` (driver decision 11:33Z).**

- It declares that the program is imported as a submodule of the package rooted at ROOT. The mode is
  opt-in and never inferred.
- It is parsed in `main()` (twin `\trusted`), not in `_parse_args`, whose twin is verified. It is passed
  to sub-invocations as `PYCSL_AS_PACKAGE_MODULE`.
- ROOT and its realpath replace the program directory among THIS check's roots only, and the candidates
  are judged as imports made from ROOT. The program's own imports resolve as before, so the emission is
  unchanged.
- `--soundness-report` lists the model assumption AS-PACKAGE-MODULE. A ROOT that does not contain the
  file exits with rc 2.
- A stdlib-named module directly under ROOT still refuses (`jobA/modes.txt`, case pk).

The mirror gates pass ROOT = `src/self-annotate/src`. It is the mirror's image of `src/pycsl`, where the
entry script `pycsl.py` makes sys.path[0], and it contains every mirror file (`src/pycsl` contains
none). The gates that pass it:

- `bin/mirror-emit-sweep.sh`;
- the shared mirror emission in `run-soundness-planes.sh`;
- check-emitted-vacuity, yield-erasure, computed-rhs-erasure, cross-module-contract-parity,
  mirror-type-only, shadowed-selfcalls, untrusted-emitted, getattr-erasure, swallowed-exceptions,
  bespoke-model-drift, trusted-frame-honesty;
- run-self-annotation-suite, bridge-roundtrip, screen/probe-conversion-candidate(s),
  self-annotate-generate.

Every one of these passes the mode ONLY for files under that root.

**Mirror files with a stdlib-named sibling.** These are the 16 files of `module6_whyml/`, whose sibling
is `types.py`:

- `__init__`, `abstract_ops`, `auto_trust`, `expr_ghost_collections`, `expr_ghost_spec_ops`;
- `expressions`, `functions`, `identifiers`, `ir_scanner`, `irx`, `preamble`;
- `scc`, `statements`, `stmt_control_flow`, `struct_format`, `types`.

They are refused in script mode and accepted in the declared mode. `jobA/modes.txt` checks scc, types
and expressions in both modes.

**Cache.** `src/pycsl/__pycache__/r613-stdlib-imports-<key40>.json`.

- The key is sha256 over: version, cache_tag, the stdlib path, both name sets, and every stdlib `.py`
  (relpath, size, mtime_ns), re-walked on each run.
- The table is used only if the stored key and the shape `{str: [str]}` match. Otherwise (absent,
  unreadable, truncated, malformed, stale) it is rebuilt and atomically replaced, so it never fails open.
- A `.json` name can never match the r12 scan.
- Cost: about 2.6 s once per interpreter. Warm cost is not measurable: 1.31 s per `--no-proof` run at
  both base and HEAD, over 5 runs each (`jobA/time-*.txt`).
- Integrity test: §6, jobC.

Docs: annotations.md, plus the static-semantics, translational and concrete-syntax (§11.3) references.
doc-coherency rc 0.

## 4. Witnesses (10180-10188, `multi_file_lib/r613/`; census rows from `_census_row`)

| id | layout | base 899b / 0057 (h / t / s) | HEAD (h / t / s) |
|---|---|---|---|
| 10180 FAIL | json + `re.py` | PROVED / VF / VF | REFUSED x3 |
| 10181 FAIL | hashlib + `_hashlib.py` | PROVED x3 | REFUSED x3 |
| 10182 FAIL | no import + `re.py` | PROVED / VF / VF | REFUSED x3 |
| 10183 FAIL | json + `sitecustomize.py` | PROVED / VF / VF | REFUSED x3 |
| 10184 FAIL | json + sourceless `re.pyc` | PROVED / VF / VF | REFUSED x3 (NONSOURCE-ARTIFACT at node `re`) |
| 10185 FAIL | dependency -> json + `re.py` | PROVED / VF / VF | REFUSED x3 |
| 10186 PASS | json + bare `re/` | PROVED / VF / VF | identical |
| 10187 PASS | json + identical `codecs.py` | PROVED / VF / VF | identical |
| 10188 PASS | json, no shadow | PROVED / VF / VF | identical |

The CPython layout for each witness (PYTHONPATH = its root) is in `cpython.txt`.

## 5. Over-refusal (static root scan `jobB/scan.txt`, plus the sweeps)

| tree | stdlib-named entries in roots | effect |
|---|---|---|
| corpus root (6244 files) | `./json` (admitted copy) for every file; per-witness roots `r326shadow` (math/os/time .py), `r611art` (hashlib.pyc/.so/pkg), `r611r12/hu` (hashlib.py), `r611r12/tok`,`tu` (tomllib), `r613/*` | 0 previously emitting files refused (0 GONE) |
| pyref (2217 files) | `./json` only | 0 refused |
| mirror (53 files) | `./json`, and `module6_whyml/types.py` (16 files) | 16 refused in script mode; 0 under the declared mode |

The pre-existing witnesses in those roots were already refused. The direct #326 / #611 / r12 check
fires first, so their census rows did not change: refusal-witness-coverage is green.

## 6. Gates

**jobB, snapshot `pycsl-u52-g3` @ f050b4ebb, cwd = the tree root, PRIO** (`witnesses-r613/jobB/`):

- byte-diff root: 3281 baseline / 3284 candidate, 0 MOVED / 0 GONE / 0 APPEARED. The 3 new files are
  the controls.
- byte-diff pyref: 2185 / 2185, 0 / 0 / 0. Baseline: v66 bd-int, the L15 emission.
- mirror: 53 emitted, `diff -rq` 0 lines, byte-diff-compare 53 / 53, 0 / 0 / 0 (vs v66 mir-int).
- fidelity: sync rc 0, mirror-check rc 0, doc-coherency rc 0.
- fast planes: 62 / 62 green.
- refusal-witness-coverage rc 0: 480 demonstrated (+1, the new site), 5 undemonstrated (ceiling 5).
- assigns-writes-survival rc 0, on a single-underscore emit dir.
- getattr-erasure rc 0.
- frontend-only 38 / 38, core-only 38 / 38.
- count-trusted rc 0 (grep 367).
- trusted-frame-honesty rc 0. Its own emitter did not pass the mode in this run: fixed in cb7f2516c and
  re-run in jobC.

**jobC** (`witnesses-r613/jobC/`, tree u52 @ cb7f2516c, oom_kill 5 -> 5):

- **Cache integrity.** 10180 and 10183 refused and 10188 emits in every state of the table. The states
  were: (a) as built; (b) truncated to 20 bytes; (c) wrong shape; (d) STALE, meaning the right shape
  with another key and an empty graph, which if trusted would have admitted `sitecustomize`; (e)
  deleted. After each one the table was rebuilt as valid JSON carrying the current key (193 entries).
- **trusted-frame-honesty**, re-run with the mode in its own emitter: rc 0, param not-lowered 86 = the
  ratchet 86, frame honesty 0/1 and 0/63.
- The jobB run of that check had read 78. That reading was from a false emission: its emitter did not
  pass the mode, so the 16 refused module6_whyml files were missing from it. This is now fixed.

## 7. Residuals

These are in the route file:

- time of check vs time of use;
- a writable pycsl install dir (a forged table carrying the right key);
- the program's runtime environment (PYTHONPATH, `.pth`, another interpreter, a case-insensitive FS);
- dynamic imports of program-chosen names.

**Documented over-refusals:**

- dead-branch imports, because the table is flow-insensitive (`java`);
- a script-dir `sitecustomize`;
- a shadow of a startup-loaded module.

**Logs:**

- `witnesses-r613/{cpython.txt,tc3-*,tc4-*,pr-*,jobA/,jobB/,jobC/}`;
- `scratchpad/u52/{A,B,C}/`;
- `/home/fabrice/git/pycsl-u52/progress.txt`.
