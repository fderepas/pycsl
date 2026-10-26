# OPEN ROUTE #393 — S1 ADMITS EVERY BUILTIN EXCEPTION BASE, BUT A SUBCLASS'S CONSTRUCTION IS LOWERED `any d` WITH NO SIGNATURE CHECK
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r393/`: `a52_X_exception_group_ctor.py`, `a53_X_unicode_decode_ctor.py`, `a54_X_exception_kwargs.py`, `e06_subclass_init_kw_only_base.py`.

```
#393 S1 ADMITS EVERY BUILTIN EXCEPTION BASE, BUT A SUBCLASS'S CONSTRUCTION IS LOWERED `any d` WITH NO SIGNATURE CHECK  [slips past S1]
  a52  class D(ExceptionGroup); D()        no_exception PROVED   CPython TypeError (__new__ takes exactly 2 arguments)
  a53  class D(UnicodeDecodeError); D("x")                       TypeError (function takes exactly 5 arguments)
  a54  class D(Exception); D(x=1)                                TypeError (takes no keyword arguments)
  e06  class D(SyntaxError); D("m", 1)                           TypeError ('int' object is not iterable)
  (The direct calls UnicodeDecodeError("x") / ExceptionGroup("m", []) / KeyError(a=1) are refused, e01-e03: only the
  subclass path is open. e05 OSError(1..6) is legal.)
  REPAIR: in the BASE-MODEL table admit a builtin exception base only with its modelled constructor: `*args` positional,
  no keywords, for BaseException / Exception and the classes whose __init__/__new__ accept any positional arity; refuse
  (or check arity at the call) for UnicodeDecode/Encode/TranslateError, (Base)ExceptionGroup, SyntaxError family,
  and refuse a keyword argument at any construction of a class whose __init__ is inherited from a builtin exception.
```
