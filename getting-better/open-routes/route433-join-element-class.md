# OPEN ROUTE #433 — str.join / bytes.join OVER ELEMENTS NOT DERIVABLY str / bytes OWES NO TypeError
**Status: REPAIRED (executor g4, driver run #3, 2026-10-28), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r433/` (9): `jj00_join_tuple_opt.py`, `jj01_join_dict_vals_opt.py`, `jj02_join_union.py`, `jj03_join_bytes_opt.py`, `jj04_join_any.py`, `jj05_join_list_int.py`, `jj06_join_opt_loop.py`, `jj10_join_bytes_into_str.py`, `oo01_join_opt.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#433 str.join / bytes.join OVER ELEMENTS NOT DERIVABLY str / bytes OWES NO TypeError   (9)
  jj05  xs: List[int]; len("".join(xs)) PROVED; f([1])                                         CPython TypeError
  jj00 Tuple[str, Optional[str]]   jj01 Dict[.., Optional[str]].values()   jj02 List[Union[str, int]]   jj03 b"".join(List[Optional[bytes]])
  jj04 List[Any]   jj06 Optional elements appended in a loop   jj10 "".join(List[bytes])   oo01 List[Optional[str]]
  REPAIR (proposed, allow-list / refuse by default): `S.join(it)` is admitted only when the element class of `it` is derived EXACTLY {str} (for a str S) / {bytes, bytearray}
  (for a bytes S); any other / underivable element class is refused under `no_exception` (TypeError).
```

## REPAIR (executor g4, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.134, translational §T.6.145)

Same position as #432's rule (src/pycsl/pycsl.py, after the hashing pass; no new def in a mirrored file, no axiom, no emission
change). ALLOW-LIST: in a function that is not `\trusted` / `\abstract` and claims TypeError, `S.join(it)` (one positional
argument) whose receiver is derived exactly `str` is ADMITTED iff the element classes of `it` (`_ei383`, through Optional
(+ None) / Union / `|` / Annotated / Final / aliases / string annotations) are derived and all `str`; a receiver derived
`bytes` / `bytearray` admits only `bytes` / `bytearray` elements. Everything else -- `None`, `int`, `bytes` into a `str`
join, `Any` (underivable), a display holding an Optional -- is REFUSED (`PYCSL-R433-JOIN-ELEMENT-CLASS`).

Witnesses 6525-6533 (the 9 red-team probes): PROVED at base, REFUSED at the candidate, each a CPython TypeError. Controls
6534 (`b"-".join(List[bytes])`), 6535 (the `List[int]` join without a claim): PROVED at base and candidate.

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

A join whose receiver is not derived as `str` / `bytes` (an unknown receiver, a `Union[str, bytes]` receiver) is not judged.
The element rule is flow-insensitive: `",".join([x])` under `if x is not None:` is still refused (over-refusal; the advice
does not suggest narrowing). `str.join` over a `List[str]` PARAMETER does not type-check at base (Why3 `array string` vs
`array int`); a display of `str` values does (the advice probe).
