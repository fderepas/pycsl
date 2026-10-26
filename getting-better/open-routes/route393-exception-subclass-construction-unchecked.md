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

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**Design: a builtin exception base is admitted only WITH its constructor model, and a construction is checked against it.**
(1) S1's BASE-MODEL table admits a builtin exception only from an allow-list (`_exok1`): the classes whose constructor accepts any
positional arity (measured on CPython 3.14: a subclass without `__init__` accepts arities 0..7 of any type) -- plus the `SyntaxError`
family, checked by shape; `(Base)ExceptionGroup`, `UnicodeDecode/Encode/TranslateError` are refused (`PYCSL-S1-UNMODELLED-BASE`: a52,
a53). (2) Route #369's constructor-arity walk reads an allow-listed base as `(self, *args)` with NO keyword (a54 `D(x=1)`,
`super().__init__(msg=x)`, `Exception.__init__(self, msg=x)`, a grandchild's keyword, `raise D(k=1)`), and a SyntaxError-family base
as `()` / `(msg)` / `(msg, <4- or 6-tuple display>)` (e06 `D("m", 1)`); a class deriving from a builtin exception whose signature is
unreadable (a `__new__` in the file MRO, class keyword, decorated `__init__`) is refused at construction
(`PYCSL-R369-CONSTRUCTOR-ARITY`). A plain file `__init__` is checked as before. Docs annotations §7.52, translational §T.6.63.
Witnesses 5620-5623 (a52, a53, a54, e06) and latents 5650-5653, all PROVED at 3b2d2e763 -> REFUSED; controls 5680, 5686 PROVED both.
Residuals: `cls(..)` / `type(self)(..)` / `functools.partial(D, ..)` constructions are not checked; a class from a user module is
checked in its own module by S1 only.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
