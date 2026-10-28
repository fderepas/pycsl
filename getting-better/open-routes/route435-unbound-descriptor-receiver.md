# OPEN ROUTE #435 — AN UNBOUND str / bytes METHOD DESCRIPTOR APPLIED TO A WRONG-TYPE FIRST ARGUMENT OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r435/` (8): `c0_str_unbound_bytes.py`, `c1_bytes_unbound_str.py`, `c09_str_lower_bytes.py`, `c10_str_strip_bytes.py`, `c13_str_upper_bytearray.py`, `c14_bytes_upper_bytearray.py`, `c15_bytes_lower_str.py`, `c18_str_upper_list.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#435 AN UNBOUND str / bytes METHOD DESCRIPTOR APPLIED TO A WRONG-TYPE FIRST ARGUMENT OWES NO TypeError   (8)
  c0   x: bytes; str.upper(x) PROVED; f(b"a")                                                 CPython TypeError (descriptor)
  c1 bytes.upper(str)   c09 str.lower(bytes)   c10 str.strip(bytes)   c13 str.upper(bytearray)   c14 bytes.upper(bytearray)
  c15 bytes.lower(str)   c18 str.upper(list)
  (route #422's row gives `str.m(x, ..)` the RECEIVER class `str` -- it reads the callee's class, not x's.)
  REPAIR (proposed, allow-list / refuse by default): `T.m(x, ..)` for T in {str, bytes, bytearray, int, ..} is admitted only when x's derived class is exactly T (or a subclass
  the file defines); otherwise refused under `no_exception` (TypeError).
```
