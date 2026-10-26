# OPEN ROUTE #410 — §7.49 (4) copy.copy(x) / copy.replace(x) "HAS x's CLASS" IGNORES __copy__ / __replace__
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r410/`: `m01_copy_dunder_copy.py`, `m06_replace_dunder.py`.

```
#410 §7.49 (4) copy.copy(x) / copy.replace(x) "HAS x's CLASS" IGNORES __copy__ / __replace__  [slips past #394]
  m01  D.__copy__ returns [1]; {copy.copy(d)} PROVED                                            TypeError
  m06  D.__replace__ returns [1]; {copy.replace(d)} PROVED                                      TypeError
  (__reduce__ / __reduce_ex__ forms m02 / m05 and copy.deepcopy m03 are refused or fail.)
  REPAIR: the source holds only when no class of x's closure defines __copy__ / __deepcopy__ / __replace__ /
  __reduce__ / __reduce_ex__; otherwise the result class is that method's annotated return, else UNKNOWN.
```
