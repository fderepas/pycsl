# OPEN ROUTE #265 — `case True:` / `case False:` / `case None:` MATCH BY EQUALITY, NOT IDENTITY

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (both rc=0; CPython 0).
Witnesses `witnesses-r265/`: m09 (`x = 1; match x: case True: return 1`), m10 (`case False` on `n: int`, n == 0).
PEP 634: the singleton literals True/False/None match by `is`. Emission `if (n = 0) then ...`. Route #90 (`is True` as
`=`) again, through the match-literal path.
Repair: singleton literal patterns lower like `is` (an int-typed subject never matches True/False; decide by the
static type or opaque), consistent with route #90's repair.

## REPAIR (2026-10-17, branch r264 off 283d1033, landed with #264)

**Rule** (inline in `pycsl.py::_run_pipeline`, beside #264's check; mirror twin `\trusted`): route #42's bool-
singleton WHITELIST, reused for the match path. A `case True:` / `case False:` (a `MatchSingleton` with a bool
value, anywhere in a case pattern) is admitted only when the `match` SUBJECT is a Python `bool` BY CONSTRUCTION — a
bool literal, a comparison/membership (`Compare`) or a `not` — AND the singleton is the top-level pattern or a
top-level or-pattern alternative. Everything else is REFUSED (`PYCSL-SEM-MATCH-BOOL-SINGLETON`): an int-typed or
unknown subject, a `bool` ANNOTATION (not a fact — route #90), a singleton nested in a sequence/class/`as`
pattern. `case None:` is untouched: it already lowers to the opaque `pycsl_none` (routes #40/#44/#50) and the
probes below FAIL there. `case 1:` against a True subject is a VALUE pattern and stays equality (PEP 634).

**Probe table** (283d1033 -> after; CPython in parentheses):

| file | shape | base | after |
|------|-------|------|-------|
| 2799 | `x = 1; match x: case True: return 1` (0) | PROVED | REFUSED |
| 2800 | `case False:` on `n: int`, `n == 0 ==> \result == 7` (0) | PROVED | REFUSED |
| 2801 | guarded `case False if n == 0:`, `n = 0` (0) | PROVED | REFUSED |
| 2802 | or-pattern `case 5 \| True:` on `x = 1` (0) | PROVED | REFUSED |
| 2803 | control: `case 0:` / `case 1:` value patterns | PROVED | PROVED |
| probe | `match 3 > 2: case True:` (1) | FAILED (type error) | FAILED (type error, admitted) |
| probe | `x = 0; match x: case None:` claiming 1 (0) | FAILED | FAILED |
| probe | `match 2 > 1: case 1:` (1) | FAILED (type error) | FAILED (type error) |

witnesses-r265/ m09/m10: PROVED at base, REFUSED after.

**Blast radius**: ZERO `case True/False/None` patterns in pycsl-reference, python-reference, the mirror,
`src/pycsl_lib` and `src/pycsl` (AST census), so the refusal costs nothing that exists. Gates shared with #264
(0 MOVED everywhere).

**Residual (completeness, not soundness)**: a bool-by-construction subject (`match a > b:`) is admitted but its
emission `((a > b) = 1)` is ill-typed in Why3, so such a match FAILS rather than proves; lowering the subject with
`to_int` would make it provable.
