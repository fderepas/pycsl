# OPEN ROUTE #415 — `%` STRING FORMATTING IS AN UNCHECKED str_mod_op
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r415/`: `l16_percent_format.py`, `n15_percent_mapping.py`.

```
#415 `%` STRING FORMATTING IS AN UNCHECKED str_mod_op  [old family]
  l16  "%d" % s (s: str)                                                                        TypeError
  n15  "%(k)s" % {"j": a}                                                                      KeyError
  (n07 "%s %s" % (a,) fails Unknown.) REPAIR: refuse `%` with a str left operand unless the format literal's
  directives are matched against the operand count / types / keys at emission time.
```
