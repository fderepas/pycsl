# OPEN ROUTE #392 — S1 AND §7.46 RESOLVE A BASE NAME TO "A FILE CLASS" WHEN A CLASS OF THAT NAME IS NESTED ANYWHERE IN THE FILE
**Status: REPAIRED, candidate (gen #37, 2026-10-26; e1 executor off 3b2d2e763 -- sound refusal, see REPAIR; repaired with routes #392 / #394 / #395). Was OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
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

## REPAIR (2026-10-26, e1 executor off 3b2d2e763, with routes #392 / #394 / #395; code + corpus + census + docs in commit 3445dc472; docs annotations §7.48 / translational §T.6.59)
**Design: ONE scope resolver, inline in `_run_pipeline` just before S1 (mirror twin `\trusted`, no new def, no emission change).** For every class header of the main file and of each dependency module, each base head name is resolved as CPython evaluates the header: the enclosing scope (a class body only when immediately enclosing), enclosing functions (`global` jumps to the module), the module (through `if` / `try` / `with` / loops; nested def / class / lambda bodies are other scopes), the builtins, a stdlib star import -> class / import / other / builtin / star / unbound (`_rb1`). S1, its star-import rule and the §7.46 hash MRO (`_bn346` / `_kb381`: a shadowed import / builtin / star base becomes the outside token `name@`) all read it; the old `ast.walk` file-class set `_fw1` and the `_bw1` / `_star1` approximations are gone. TC and GD already resolved the import first and are unchanged. NEW latent found: `from typing import TypedDict` + nested `class TypedDict` + `class T(TypedDict)` hashed `{t}` PROVED (S1 admits the modelled TypedDict base; the hash MRO took the nested class) -> corpus 5554, now refused.
Witnesses: a04 5550, c93 5551, c94 5552, c98 5553, new latent 5554. Control 5590.
Gates (candidate vs base worktree at 3b2d2e763): root byte-diff 2423 -> 2426 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (+3 controls); pyref 2186 -> 2186, 0/0/0; mirror 53/53 0/0/0 (no OWED proof); `pycsl_lib` --no-proof screen identical (104 files). Every witness PROVED at base (rc=0) and is REFUSED on the candidate (rc=1); controls 5590-5592 PROVED at base and candidate. Census rows written with `_census_row` (31 new; the 90 `is HASHED by` rows re-measured: message extended, prefix identical).
