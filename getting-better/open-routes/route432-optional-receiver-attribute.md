# OPEN ROUTE #432 — AN Optional / Union RECEIVER OF AN ATTRIBUTE OR METHOD ACCESS OWES NO AttributeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r432/` (8): `on00_strip.py`, `on05_method.py`, `on07_dict_get.py`, `on09_int_bitlen.py`, `on10_upper_ens.py`, `on11_union_int_str_upper.py`, `on13_pipe_none.py`, `op16_upper_opt.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#432 AN Optional / Union RECEIVER OF AN ATTRIBUTE OR METHOD ACCESS OWES NO AttributeError   (8)
  on00  x: Optional[str]; len(x.strip()) under no_exception \all PROVED; f(None)              CPython AttributeError
  on05 user method on Optional[C]   on07 Optional[dict].get   on09 Optional[int].bit_length   on10 .upper in an ensures-bearing f
  on11 Union[int, str].upper   on13 `str | None` (PEP 604) .lower   op16 Optional[str].upper
  (CONTRAST: all 18 Optional/Union OPERATOR probes un00-un17 (+ < - * [] range abs // aug-assign) are REFUSED; only the
  attribute / method-call receiver is unchecked.)
  REPAIR (proposed, allow-list / refuse by default): An attribute load / method call whose receiver's derived class set contains NoneType (or more than one class of which
  some lacks the attribute) is admitted only where the receiver is flow-narrowed (`is not None` / isinstance guard on the
  path) or under an obligation; otherwise refused under `no_exception` (AttributeError). Allow-list the admitted forms.
```
