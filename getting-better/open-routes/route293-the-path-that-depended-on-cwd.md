# OPEN ROUTE #293 — os.path.relpath IS MODELLED PURE BUT READS THE CWD
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r293/`. os001/os003 `r1 = relpath(s, "/usr"); os.chdir("/"); r2 = relpath(s, "/usr"); #@ check r1 == r2` proves; CPython differs. `_OS_PATH_PURE_STR` includes relpath (and possibly abspath/realpath/expanduser) whose result depends on the cwd/home/filesystem. Repair: make cwd-dependent path functions opaque per call (or depend on a modelled cwd), census `_OS_PATH_PURE_STR`.

## REPAIR (2026-10-20, executor rA off 7313506b; commit 79a2d92f)
Probe table (rc; CPython ground truth in each corpus file's `__main__`):

| shape (`check r1 == r2` across `os.chdir`) | 7313506b | after |
|---|---|---|
| `relpath("a", "/")` (os001 / 3356) | PROVED | FAIL |
| `relpath(s, "/usr")` (os003 / 3357) | PROVED | FAIL |
| census: `abspath`/`realpath`/`expanduser` (impure table), `os.getcwd()`, `os.path.expandvars`, `exists`, 1-arg `relpath`, `str(Path.cwd())` | FAIL | FAIL |
| control: `normpath`/`basename`/`dirname`/`join` equal across `chdir` (3358) | PASS | PASS |

Rule (table edit of the `ExpressionsMixin` class constants; check-self-annotate-sync green): `relpath` moves from
`_OS_PATH_PURE_STR` to `_OS_PATH_IMPURE_STR` (a plain `val`, fresh per call). CENSUS of the pure list
against CPython 3.14 `posixpath`: `basename`, `dirname`, `normpath`, `split`, `splitext`, `splitdrive`,
`join` (the `val function` set, incl. `path_join_op` for `Path /`) never call `os`; `relpath` calls
`abspath` -> `os.getcwd()`. `pathlib` `.parent/.stem/.name/.suffix` are lexical; `.resolve()` and the
`is_*`/`exists` predicates were already plain `val`s. Every other `os`/`os.path` call (getcwd,
expandvars, ...) takes the generic dotted-call fallback, a plain `val`.
Blast radius: corpus root 0 MOVED for this route, pyref 0, mirror 0 (no `relpath` user).
Gates (logs under the rA scratchpad; all heavy jobs via heavy.sh): witnesses at 7313506b vs after in
the table; byte-diff-sweep base/after rc=0 (2510 / 2529 sources); byte-diff-compare root rc=0 with ONE
declared mover (1915, below), pyref rc=0 (2186/2186, 0 MOVED / 0 GONE / 0 APPEARED); mirror-emit-sweep
base/after rc=0, compare `--min-files 45`: 1 MOVED (`frontend__pure_ast`, route #291, below), 0 GONE,
0 APPEARED; check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53);
refusal-witness census +15 rows (3340-3344 REFUSAL, 3346-3350/3352-3354/3356-3357 VERIFY-FAIL) via
`--append-new` (that run also found 234 pre-existing FAIL witnesses with no row at 7313506b — not
appended here, out of scope; reported to the driver); run-soundness-planes.sh --slow rc=1 -> 82/84 green; vacuous-drivers (3358) and hashed-literal-purity
(re-keyed baseline rows for the format-keyed struct symbols) fixed and re-run rc=0; assigns-writes-survival
TRAP 1447 > 1445 is identical at 7313506b (pre-existing).
Residuals: none known.
