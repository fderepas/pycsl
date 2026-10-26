# OPEN ROUTE #392 — S1 AND §7.46 RESOLVE A BASE NAME TO "A FILE CLASS" WHEN A CLASS OF THAT NAME IS NESTED ANYWHERE IN THE FILE
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r392/`: `a04_H_shadow_nested_cls.py`, `c93_shadow_exception_getattr_args.py`, `c94_shadow_class_in_method.py`, `c98_shadow_star_import.py`.

```
#392 S1 AND §7.46 RESOLVE A BASE NAME TO "A FILE CLASS" WHEN A CLASS OF THAT NAME IS NESTED ANYWHERE IN THE FILE  [slips past S1 + #381]
  a04  `from collections import UserList`; `def _unused(): class UserList: pass`; `class D(UserList)`; {d} PROVED  CPython TypeError
  c93  same with UserDict (D defines __init__ + super())                                                     TypeError
  c94  the shadowing class is nested in a METHOD of another class                                            TypeError
  c98  `from collections import *` + nested `class OrderedDict` (also defeats the star-import refusal)        TypeError
  WhyML: `{d}` lowers to `any int` (iter_length) with no goal. S1 (`_fw1` = every ClassDef in ast.walk) skips the base; the
  §7.46 hash MRO walk takes the nested file class (hashable). (Refused correctly: c95 `if False: class deque`, c96 shadow in
  a dependency module, c97 nested `class dict` for a builtin base, c90/c91/c92: TC and GD resolve the same base correctly.)
  REPAIR: resolve a base by SCOPE: only MODULE-LEVEL class statements shadow an import / builtin at module scope (a class
  nested in a def / method body is a local); one resolver shared by S1, §7.46, TC and GD (the latter two already get it right).
```
