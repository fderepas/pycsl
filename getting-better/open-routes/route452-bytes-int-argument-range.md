# OPEN ROUTE #452 — bytes / bytearray find / count / rfind / `in` with an int argument outside 0..255 (ValueError)
**Status: REPAIRED (executor r3, driver run #3, 2026-10-29), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r452/` (13): `c14_y000.py`, `c14_y001.py`, `c14_y002.py`, `c14_y003.py`, `c14_y004.py`, `c14_y005.py`, `c14_y006.py`, `c14_y020_realistic_header.py`, `c14_y021_realistic_count.py`, `c5_y000_bytes_find_int.py`, `c5_y001_bytes_count_int.py`, `c5_y002_bytes_rfind_int.py`, `c5_y010_bytes_in_int.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F9 -- bytes / bytearray find / count / rfind / `in` with an int argument outside 0..255 (ValueError)   (13)
  EXEMPLAR c14/y020_realistic_header.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(sep: int) -> int:
    |     data = b'GET / HTTP/1.1'
    |     return data.find(sep)
    CPython 3.14: f(0x100)  ->  VIOLATION ValueError byte must be in range(0, 256)
  MECHANISM: (bytes, find / count / rfind) rows take code BI (bytes-like or int) with no range obligation on the int; `n in
  <bytes>` likewise. The call lowers to an opaque `data_find_1 sep` (receiver erased, mlw/y020). CPython raises
  ValueError 'byte must be in range(0, 256)' for an int outside 0..255. (A `b: bytes` PARAMETER does not type-check
  -- `unbound type symbol 'array'` -- so the probes use bytes literals / locals.)
  REPAIR: OBLIGATION on the int arm of every BI-coded bytes argument (find rfind count index in, and bytearray append /
  insert / remove when rows exist): `0 <= n < 256` (ValueError), same shape as #434's ord obligation.
  MEMBERS: c14/y000.py c14/y001.py c14/y002.py c14/y003.py c14/y004.py c14/y005.py c14/y006.py c14/y020_realistic_header.py c14/y021_realistic_count.py c5/y000_bytes_find_int.py c5/y001_bytes_count_int.py c5/y002_bytes_rfind_int.py c5/y010_bytes_in_int.py
```

## REPAIR (executor r3, driver run #3, 2026-10-29, off db6c57253; annotations §7.202, translational §T.6.212)

Code inline at the end of the per-function signature pass of `_run_pipeline` (after routes #440 / #441, over the
same derived classes `_ty383` / `_CN440` / `_rs440`; mirror twin `\trusted`, no new def, no axiom, no emission change).
A call `R.find / rfind / count / index / rindex(a, ..)` or a comparison `a in R` / `a not in R` with `R` derived `bytes` /
`bytearray` admits `a` iff its classes are all `bytes` / `bytearray` / `bool`, or `a` is an int literal in 0..255; an int /
underivable `a` is refused under a claim covering ValueError, another class under one covering TypeError
(`PYCSL-R452-BYTE-RANGE`). DESIGN NOTE: an obligation `0 <= n < 256` (the #434 / #436 shape) needs the receiver's class in
Module 6, where a bytes value is an `array int` like a list (the emitter cannot tell `b.count(n)` from `xs.count(n)`); the
refusal is decided where the class IS derived, moves no emission, and is fail-closed over every node of the body
(comprehensions and lambdas included), so no erased-obligation census is needed. A guarded computed int is refused
(over-refusal, cost measured 0 in corpus and mirror).
Witnesses 7016-7022 (7 of the 13 probes; all 13 PROVED at base and are REFUSED). Controls 7023 (`find(71)` / `count(0)` /
`rfind(255)`), 7024 (`71 in b"GET"`): PROVED at base and candidate.

GATES (one candidate, one battery for #447 / #451 / #452 / #454 / #456 / #459; see the README run-#3 r3 entry): fidelity sync / mirror-check rc=0; root corpus 2569 base -> 2581 candidate .mlw, 0 MOVED, 3 GONE (5066 / 5071 / 5072, expected FAIL route-#375 witnesses `[*self]` / `(*self,)` / `g(*self)` on a field-less class: VERIFY-FAIL -> REFUSED by #454), 0 APPEARED; pyref 2186 / 2186 0 / 0 / 0; mirror 53 / 53 0 / 0 / 0 (no OWED proof); planes / ledgers: see the README entry.

## RESIDUALS: a computed int in range is not admitted (no obligation form); `bytearray.append / insert / remove` have no
signature row (refused by #440 already).
