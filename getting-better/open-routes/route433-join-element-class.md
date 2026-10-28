# OPEN ROUTE #433 — str.join / bytes.join OVER ELEMENTS NOT DERIVABLY str / bytes OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
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
