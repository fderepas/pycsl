# OPEN ROUTE #270 — #264's DEFINITE-ASSIGNMENT ANALYSIS MISSES EXCEPTION EDGES FROM CALLS (AND TREATS GENERATORS AS NO-RETURN)

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 4; driver-reproduced at HEAD eced7036 (rc=0; CPython
UnboundLocalError). Witnesses `witnesses-r270/`:
- a20: `if c: y = 2`; `try: C.g(1)` (declared `raises ValueError when x > 0`) `except ValueError: pass else: y = 1`;
  `return y` with `ensures \result >= 0` proves. The analysis (pycsl.py ~2524-3005) adds exception edges only from
  local read/write/nop ops; a call reading no local creates none, so the handler path is invisible.
- a25: `fail()` is a GENERATOR (`yield 1; raise ValueError`) — treated as never-returning by #264's no-return rule
  (body ends in raise, no return) although calling a generator only builds it.
Repair: every potentially-raising operation (calls, division, subscripts, attribute access...) inside a `try` adds
an exception edge carrying the pre-state; generator functions are never "no-return".

## REPAIR (2026-10-17, branch r270 off c9d7f157, landed with #271)

**Rule** (inline in `pycsl.py::_run_pipeline`, inside route #264's must-assign block; mirror twin `\trusted`; no
new `def`):
1. **Every potentially-raising operation inside a protected region adds an exception edge** carrying the state at
   that point. While the exception stack is non-empty (a `try` body / `else` / handler under a `finally`, a `with`
   body), EVERY expression node the CFG builder visits appends a `nop` op after its children — except a literal, a
   `lambda` (creating one cannot raise), a walrus (its value gets its own edge) and a local read (its `use` op
   already had the edge). An attribute/item STORE or DELETE target and every `match` pattern add one too. Outside a
   protected region nothing changes (an op's exception list is empty there), so the graph grows only inside `try`/
   `with`.
2. **A generator or a coroutine is never no-return**: the no-return census counts an own `yield`/`yield from` like a
   `return`, and an `async def` is never in it — calling either only builds an object.

**Probe table** (c9d7f157 -> after; CPython raises `UnboundLocalError` for every FAIL row):

| file | shape | base | after |
|------|-------|------|-------|
| witnesses-r270/a20 | `try: C.g(1)` (raises) `except: pass else: y = 1`; `return y` | PROVED | REFUSED (UNBOUND-LOCAL) |
| witnesses-r270/a25 | `else: fail()` where `fail` is a generator ending in `raise` | PROVED | REFUSED (UNBOUND-LOCAL) |
| 2900 | a20 as a corpus witness | PROVED | REFUSED |
| 2901 | a25 as a corpus witness | PROVED | REFUSED |
| 2902 | handler reached only through `C.g(1)` reads `y` (handler was UNREACHABLE) | PROVED | REFUSED |
| 2904 | control: handler AND `else` both bind `y` | PROVED | PROVED |

(A module-level-function variant of 2900 was tried and dropped: it fails `--type-only` at base for an unrelated
reason, so it is not a witness.)

**Blast radius**: corpus root 0 MOVED / 0 GONE / 0 APPEARED (+4 new PASS controls 2904/2909/2910/2911, +1 2912);
pyref 2186/2186 0 MOVED / 0 GONE; mirror 53/53 0 MOVED / 0 GONE (no mirror re-proof owed). A refusal-MESSAGE diff
(base vs after, `--no-proof`) over every corpus and `pycsl_lib` file containing `try:`/`with`/`yield` (197 + 10
files): only the two `multi_file_lib/r257_*lib.py` helpers move, and they move by route #271's rule, not this one.

**Residuals** (stated): exceptions raised by `__exit__` at the normal end of a `with` body and by implicit protocol
calls (`__bool__` of a condition, `__iter__`/`__next__` of a `for`) are covered only through the edges the region
already has (each carries a state no larger than the one at the raising point, so must-assign stays sound); the
#264 residues (closure-cell reads, deferred generator-expression parts, `self.<m>` no-return override) are unchanged.

**Gates** (logs under the executor scratchpad `r270/`): witnesses base/after `wit/summary.txt`; corpus root 1755 ->
1760 .mlw (+5 new PASS controls 2904/2909/2910/2911/2912), 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186/2186 0 MOVED /
0 GONE; mirror 53/53 0 MOVED / 0 GONE (no mirror re-proof owed); refusal-witness census +7 own rows (via the plane's
`_census_row`), 229 demonstrated / 5 undemonstrated; advice audit +3 FOLLOWABLE (route #271's three messages);
`run-soundness-planes.sh` 61/61 and `--slow` 84/84 green; `check-self-annotate-sync.sh`,
`self-annotate-mirror-check.sh`, `check-mirror-coverage.py` rc=0. Ledger 3 (no axiom), no new `def`.
