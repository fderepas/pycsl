# Run #8 executor u50: S1 refusal-only repairs (route #611 r12; batch B = u48 R1 / R2 / R4)

Branch `run8-u50` (worktree `/home/fabrice/git/pycsl-u50`), base `0057c8b94`. Commit only, nothing pushed.
`\trusted` 367 (unchanged), proof-axiom ledger 3 (`src/pycsl/proof_axiom_allowlist.py` untouched), oom_kill 0 at
the start and end of every heavy job (`scratchpad/u50/oom-*.txt`).

## Commits

| commit | content |
|---|---|
| `89e942ec4` | task 1: route #611 r12 rule, witnesses 10124-10129, census rows, docs, probe kit |
| `69529e2de` | task 1 follow-up (driver review cr63): `_co_code_adaptive`, unlistable cache dir, latent stale timestamp pyc, no `with ... as`, dotted-path witnesses 10126-10128, residuals documented (`R12-FOLLOWUP`) |
| `88d9fb8c3` | census rows for 10124-10127 regenerated with `_census_row` |
| `4740c6c0d` | task 2: batch B (R1, R2 narrowed, R4 ported from run7-u48 e4e1bea94; R3 dropped), witnesses 10130-10136, census rows |
| (this file) | report |

## Task 1: route #611 r12 (forged `__pycache__` pyc)

**Rule** (in `_resolve_module_path`, `src/pycsl/frontend/ir_resolve.py`; its mirror twin is `\trusted`; refusal-only and fail-closed). Code: `PYCSL-SEM-IMPORT-PYCACHE-UNVERIFIED`.

**Which modules are checked:**
- the resolved hit;
- each parent `__init__.py` on its dotted path;
- every `.py` of an admitted stdlib-named package copy.

**Which caches are candidates.** Every cache name the running interpreter's loader can derive:
- `__pycache__/<m>.<cache_tag>.pyc`;
- `<m>.<cache_tag>.opt-<N>.pyc` for any N >= 1. `-OOO` loads `.opt-3`, and the loader compiles at level 2 for every N >= 2;
- the same names under pycsl's own `sys.pycache_prefix`.

**Which candidates are skipped.** Only those CPython can never load: shorter than 16 bytes, wrong magic, or unknown flag bits.

**The check.** Every other candidate is unmarshalled and must equal `compile(source, path, 'exec', dont_inherit=True, optimize=min(N, 2))`:
- every `co_*` attribute and `_co_code_adaptive` must match;
- the comparison recurses through `co_consts`, with exact constant types, float / complex bits, and frozenset and slice constants;
- `co_filename` is compared after the same rewrite that `_imp._fix_co_filename` applies.

This covers unchecked and checked hash-based pycs, and timestamp pycs whether their header matches the source or not. An unlistable `__pycache__` refuses the import, as does an unreadable cache.

**Rule 30: which file does CPython actually load?** `SourceLoader.get_code` takes the cache without reading the source in three cases:
- an unchecked hash pyc;
- a checked one under `--check-hash-based-pycs never`;
- a timestamp pyc whose header matches the source's stat.

A stale timestamp pyc goes live later through `touch -d`, `cp -p` or `rsync -t`. SOURCE_DATE_EPOCH only changes which kind of pyc `py_compile` writes; that is covered.

### CPython probes

The 22 probes are in `getting-better/open-routes/witnesses-r611r12/`:
- `make.sh` builds them;
- `cpy.sh` runs them under real CPython, ulimit'd, with `-B`;
- `pyc.sh` runs them through pycsl;
- results are in `cpython-results.txt` and `pycsl-verdicts.txt`.

Each probe ran under CPython in six configurations: default, -O, -OO, -OOO, `--check-hash-based-pycs never` and `--check-hash-based-pycs always`.

- **CPython runs forged bytecode** (VIOLATION in at least one configuration):
  - A1 (hashlib copy, unchecked);
  - A2 (forged timestamp);
  - A3 (checked, bad hash; only under `never`);
  - A6 / A7 / A9 (opt-1 / opt-2 / opt-3, only under -O / -OO / -OOO);
  - J1 (json copy, `__init__`);
  - N1 (plain dependency);
  - T1 (tomllib copy, submodule `_parser`).
- **pycsl at HEAD refuses exactly that set, with PYCACHE-UNVERIFIED.** Every genuine, stale or other-version cache is accepted (A4 A5 A5o A5r A5u A8 J2 N2 T2; A5r was written by real CPython at default / -O / -OO / -OOO).
- **At BASE 0057c8b94:**
  - **N1 and T1 PROVE.** These are live pre-existing false proofs: CPython returns 3 instead of 2, and tomllib runs the forged loader.
  - A* were held only by the rebound-name rule, and J* only by route #305.
- These first-round probe verdicts are from `89e942ec4`. The follow-up's stale-pyc change refuses A4 too (see the follow-up section below).
- **Main tree** (live caches, exact rule code via `blk.py`, `maintree-scan.txt`):
  - at `89e942ec4`: all 241 source modules with a cache, plus the repo-root `json/` package, are accepted;
  - after the follow-up: 25 of the 242 are refused, all honestly stale headers (follow-up below).

### Witnesses (x3 models: hoare / typed / store)

| file | BASE | HEAD |
|---|---|---|
| 10124 hashlib copy + forged unchecked pyc (`--import-path …/r611r12/hu`) | refused (rebound-name) | REFUSED PYCACHE-UNVERIFIED x3 |
| 10125 tomllib copy + forged `_parser` cache (`…/tu`) | hoare PROVED; typed / store VERIFY-FAIL | REFUSED x3 |
| 10126 dependency + forged unchecked pyc (dotted import; CPython prints 3) | hoare PROVED (false proof); typed / store VERIFY-FAIL | REFUSED x3 |
| 10127 dependency + forged `.opt-3` pyc (CPython -OOO prints 3) | hoare PROVED (false proof); typed / store VERIFY-FAIL | REFUSED x3 |
| 10128 CONTROL dependency + genuine `.pyc` / `.opt-1.pyc` | hoare PROVED; typed / store VERIFY-FAIL | identical |
| 10129 CONTROL tomllib copy + genuine caches | hoare PROVED; typed / store VERIFY-FAIL | identical |

- The typed / store VERIFY-FAIL is pre-existing and identical at base: "This function depends on external variables, it cannot be used as pure", for a module-qualified import stub.
- The route #611 regression witnesses are still refused NONSOURCE-ARTIFACT x3: 10120, 10122, 10123, w1, w2, w3, r16, r17, j04 and r19.
- The controls 10116, 0443 and w4 still PROVE x3.
- The 10124-10129 rows are from runs at `89e942ec4` (the 10126-10128 rows used the pre-follow-up `--import-path` form):
  - logs: `scratchpad/u50/t1w-emit*`, `t1w-prove*`, `t1w-base-v1*`, `t1w-base2/`, `t1w-head2/`;
  - verdicts: `classify.sh`.
- After the follow-up (dotted-path form, final code):
  - CPython: 10126 prints 3, 10127 prints 3 under -OOO, 10128 prints 2;
  - refused / emitted status, re-measured by census and sweep: 10124-10127 have REFUSAL census rows (`t1-census2.tsv`), and the C sweep (`g2/C-root.txt`) emits exactly 10128 and 10129 (3275 to 3277).

### Gates on snapshot `pycsl-u50-s2` @ `88d9fb8c3` (`scratchpad/u50/g2/`, `gate.sh`)

- **Corpus byte-diff** vs `run8/base8/bd`: root 3275 to 3277 (the 2 controls), **0 MOVED / 0 GONE / 0 APPEARED**; pyref 2185 / 2185, 0 / 0 / 0.
- **Mirror** vs `base8/mir`: 53 / 53, **0 diff lines**. Mirror-inert, so no re-proof is owed.
- **Fidelity:** sync rc 0, mirror-check rc 0, doc-coherency rc 0.
- **Fast planes:** `run-soundness-planes.sh` **62 / 62 green** (`g2/P-planes.log`).
- **Individual planes:** all rc 0 — refusal-witness-coverage (476 demonstrated / 5, ceiling 5), getattr-erasure, frontend-only-conformance 38 / 38, core-only-conformance 38 / 38, assigns-writes-survival (HOLE 0), trusted-frame-honesty, count-trusted-directives.
- **The first gate**, `g1` on `89e942ec4`, was 60 / 62. Both reds are fixed in `69529e2de`:
  - `check-dropped-mutation` CTXBIND 53 > 51, caused by my two `with open() as`;
  - `check-corpus-executes`: 10128 was not loadable under CPython.

### Follow-up (driver review cr63) and the over-refusal it costs

- **R1:** `_co_code_adaptive` must be equal. It costs 0 genuine caches.
- **Q3:** an `os.listdir` OSError now refuses instead of crashing.
- **Residual 3:** a timestamp pyc whose header does not match the current stat is now VALIDATED.
- **Measured over-refusal** (`maintree-scan.txt`):
  - **25 of 242** main-tree caches are refused, all honestly stale headers: 13 in `src/pycsl`, 2 in `src/pycsl_lib`, 5 mirror sources and 5 corpus programs;
  - with those 25 caches copied into the snapshot (`stale.sh`), the corpus root and pyref are still 0 / 0 / 0;
  - **mirror: 3 of 53 become unemittable** (GONE): `Module6_WhyMLTranspiler`, `proof2why3__crosscheck_ir`, `pycsl` (`g2/stale-mir.txt`).
  - So in the main tree today the mirror sweep would lose 3 files until the stale caches are refreshed or deleted. CPython refreshes a stale cache whenever it imports the module. Fresh worktrees are unaffected.
  - The message text says so ("an honestly STALE one ... FIX: delete the `__pycache__` entry"). Keeping it is for the driver to decide.
- R2 (`localspluskinds`), R3 (constant sharing), TOCTOU, the `-m` `__init__` chain and the runtime pycache prefix are documented in the route file and the code comment.

### Residuals (open)

- The program's runtime PYTHONPYCACHEPREFIX, another interpreter's cache tag, and `python -m prog`: the main file's cache and the package chain above it are not checked.
- TOCTOU: a cache that appears after verification.
- Fields not compared: `localspluskinds`, and constant identity / sharing.
- Over-refusals (all fail-closed): a stale checked-hash pyc, `-X no_debug_ranges` caches, an unreadable cache, a different patch release, and the stale-timestamp cost measured above.
- Adjacent, not a pyc issue, not repaired: a stdlib module transitively imported by an admitted copy, or by the real stdlib (`json` imports `re`), can be shadowed by a local `re.py` that the program never imports itself.

## Task 2: batch B (rules ported into `_run_pipeline`, mirror twin `\trusted`)

R1 `PYCSL-R608-PYVAL-SLICE`, R2 `PYCSL-R608-LAUNDER-OWN-RESULT-CLAUSE` (narrowed) and R4 `PYCSL-CV14-STR-RFIND-RECEIVER-DROPPED` were applied from the run7-u48 diff. `pycsl.py` is identical between 06cb88013 and the base. **R3 was dropped** (`scratchpad/u50/port_task2.py`).

| file | BASE (hoare / typed / store) | HEAD |
|---|---|---|
| 10130 R1 `v[0:0] == ""` (CPython VIOLATION) | VERIFY-FAIL x3 (L3-tc) | REFUSED PYVAL-SLICE x3 |
| 10131 R1 CONTROL, iterated with an invariant | not run at base: refusal-only, so emission and proof equal base | PROVED / FAIL / FAIL |
| 10136 R1 CONTROL, narrowed, no slice | same | PROVED x3 |
| 10132 R2 `\result * 0 == ""` (CPython VIOLATION) | VERIFY-FAIL x3 | REFUSED LAUNDER-OWN-RESULT-CLAUSE x3 |
| 10133 R2 CONTROL, no `\result` clause | PROVED / FAIL / FAIL | identical |
| 10134 R4 `x.rfind("a") == y.rfind("a")` (CPython VIOLATION) | VERIFY-FAIL x3 | REFUSED RFIND-RECEIVER-DROPPED x3 |
| 10135 R4 CONTROL `x.find` | PROVED x3 | PROVED x3 |

Logs: `scratchpad/u50/t2w-base/`, `t2w-head/`, `c1v-head/` (10131 = `c1a`, 10136 = `c1b`), and census rows `t2-census.tsv`.

### Gates on snapshot `pycsl-u50-s3` @ `4740c6c0d` (`scratchpad/u50/g3/`)

- **Corpus byte-diff** vs `base8/bd`: root 3275 to 3281 (the 6 new controls: 10128, 10129, 10131, 10133, 10135, 10136), **0 MOVED / 0 GONE / 0 APPEARED**; pyref 2185 / 2185, 0 / 0 / 0.
- **Mirror:** 53 / 53, **0 diff**.
- **Fidelity:** rc 0 x3.
- **Fast planes:** **62 / 62 green** (`g3/P-planes.log`).
- **Individual planes:** all rc 0 — refusal-witness-coverage **479** demonstrated (+3, one per new raise site) / 5 undemonstrated (ceiling 5), getattr-erasure, frontend-only 38 / 38, core-only 38 / 38, assigns-writes-survival (HOLE 0), trusted-frame-honesty, count-trusted-directives (grep 367).
- `--slow` was not run (the driver runs it).

## Every log

All logs are under `/home/fabrice/git/pycsl-u50/scratchpad/u50/`:
- probes: `probes/`, `pyc-base*`, `pyc-head*`, `probe-verdicts*.txt`, `maintree-scan*.txt`;
- witnesses: `t1w-*`, `t2w-*`, `c1v-head/`;
- census: `t1-census*.tsv`, `t2-census.tsv`;
- gates: `g1/` (superseded), `g2/` (task 1 + stale impact), `g3/` (task 2), each with a `summary.txt`;
- scripts: `gate.sh`, `stale.sh`, `wit.sh`, `classify.sh`, `census_rows.py`.
