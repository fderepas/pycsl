# OPEN ROUTE #434 — ord() OF A STRING NOT OF LENGTH 1 OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r434/` (7): `bb02_ord_long.py`, `or0_ord_empty.py`, `or1_ord_lit2.py`, `or2_ord_slice.py`, `or4_ord_upper_sz.py`, `or6_ord_strip.py`, `or8_ord_join.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#434 ord() OF A STRING NOT OF LENGTH 1 OWES NO TypeError   (7)
  or2  ord(s[0:2]) PROVED; f("abc")                                                            CPython TypeError
  bb02 ord of a 2-char argument   or0 ord("")   or1 ord("ab")   or4 ord(s.upper()) ("ß" -> "SS")   or6 ord(s.strip())
  or8 ord("".join(..))
  REPAIR (proposed, allow-list / refuse by default): `ord(s)` with s a str owes `len(s) == 1` (bytes / bytearray: likewise) under `\all`; register it with the erased-obligation
  census like the #417 rows.
```
