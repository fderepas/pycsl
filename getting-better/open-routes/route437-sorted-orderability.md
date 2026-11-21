# OPEN ROUTE #437 — sorted() OVER ELEMENTS NOT TOTALLY ORDERED OWES NO TypeError
**Status: REPAIRED (executor g4, driver run #3, 2026-10-28), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r437/` (10): `oo12_sorted_tuple_str_opt.py`, `x04_sorted_optional.py`, `x05_sorted_tuple_dict.py`, `z03_sorted_tuple_obj.py`, `z04_sorted_tuple_opt.py`, `z06_sorted_tuple_str_dict.py`, `z07_sorted_opt_str.py`, `z09_sorted_tuple_list_dict.py`, `z12_sorted_tuple_dict_rev.py`, `z14_sorted_list_opt.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#437 sorted() OVER ELEMENTS NOT TOTALLY ORDERED OWES NO TypeError   (10)
  z04  xs: List[Tuple[int, Optional[int]]]; sorted(xs) PROVED; [(1, 1), (1, None)]            CPython TypeError
  x04 List[Optional[int]]   x05 / z06 / z09 / z12 tuples ending in a dict (reverse= too)   z03 tuple of a user class without
  __lt__   z07 Optional[str]   z14 list of Optional   oo12 Tuple[str, Optional[int]]
  REPAIR (proposed, allow-list / refuse by default): `sorted(it)` / `list.sort()` / min / max (no key=) are admitted only when the element class is in a totally-ordered
  allow-list (int, bool, str, bytes, float(*), tuples whose every component class is admitted, user classes with a
  verified __lt__); otherwise refused under `no_exception` (TypeError). A key= callable: same rule on its result class.
```

## REPAIR (executor g4, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.135, translational §T.6.146)

Same position as #432's rule (src/pycsl/pycsl.py; no new def in a mirrored file, no axiom, no emission change). ALLOW-LIST:
in a function that is not `\trusted` / `\abstract` and claims TypeError, `sorted(it)`, `L.sort()` (L derived a list),
`min(it)` / `max(it)` and `min(a, b, ..)` / `max(a, b, ..)` are ADMITTED iff the compared values are derived and TOTALLY
ORDERED among themselves: all numbers (int / bool / float), all `str`, all bytes / bytearray, all parameterised tuples whose
components at each position are again admitted (`Tuple[T, ...]`: T everywhere), or all parameterised lists of admitted
elements; a mapping's `.items()` compares its distinct keys only. A `key=` must be `len` / `abs` / `int` / `float` / `str` /
`ord`, or a one-parameter lambda whose body is the parameter, `p[i]` of tuple elements, arithmetic over numeric elements,
or otherwise has derived admitted classes. Everything else (None, a dict / set, a user class with or without `__lt__`,
`Any`, an un-parameterised tuple / list, a mix of groups, underivable values) is REFUSED (`PYCSL-R437-UNORDERED-ELEMENTS`).

Witnesses 6536-6545 (the 10 red-team probes): PROVED at base, REFUSED at the candidate, each a CPython TypeError.
Controls 6546 (`sorted(List[int])`, `max(a, b)` / `min(a, b)` over ints), 6547 (an Optional sort under a claim not covering
TypeError): PROVED at base and candidate.

GATES (final candidate = commit a2749e12d + this commit's census / audit rows; logs getting-better/systematic-soundness-r3/g4-r432-437/gates/):
fidelity check-self-annotate-sync rc=0, self-annotate-mirror-check rc=0; root byte-diff vs the driver's 78b519f63 base sweep
(v8/cb): 2518 -> 2531 .mlw, 0 MOVED / 1 GONE (4810, expected FAIL: FAIL at base -> REFUSED by #433, `''.join([self])`) /
0 APPEARED, 14 new sources, rc=0 with --expect-gone; pyref 2186 / 2186 0/0/0 rc=0; mirrors 53 / 53 0/0/0 rc=0 (own base
sweep; no mirror refusal, no OWED proof); pycsl_lib refusal screen identical (104 files); planes (fast 61) 61/61 rc=0;
refusal-witness-coverage rc=0 (334 demonstrated, +3); refusal-advice-audited rc=0 (162 audited, +3 FOLLOWABLE: advice/
a432_*, a433_*, a437_* all PROVED); getattr-erasure / clause-survival --emit-dir / assumed-facts --emit-dir /
open-route-carriers / doc-coherency rc=0. Census: 37 new rows (36 REFUSAL + 6519 VERIFY-FAIL) via the tool's _census_row
(census.py; `--append-new` was aborted: it would also run 329 older row-less witnesses), 4621 re-measured (erased-value
message -> #437 `max(self, 0)`, REFUSED both) and 4810 (VERIFY-FAIL -> REFUSAL). Cost measured on the 902 claimed corpus
files (no-proof screen, base vs candidate): exactly 4621 / 4810 change; a first candidate also refused 3282 (PASS,
`(rec.get(..) or {}).get`) and 3345 (PASS, `key=lambda v: v + 1`) -- fixed (an `or`'s earlier operands are not None; a
lambda key's arithmetic over numbers is a number) before landing. \trusted count 442 unchanged; no axiom.

## RESIDUALS (honest)

User classes with a verified total `__lt__` are refused (over-refusal; no corpus file pays it). Sorting tuples of distinct
values that never reach a non-ordered position (`sorted(set_of_tuples)` with distinct first components) is refused unless
it is a mapping's `.items()`. `heapq` / `bisect` / `list.index`-style comparisons and `max(..., key=...)` with a non-builtin
callable are outside this rule (a key callable other than the listed builtins / lambdas is refused).
