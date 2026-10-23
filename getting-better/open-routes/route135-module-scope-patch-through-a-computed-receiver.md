# ROUTE #135 — a module object reached through a CALL (or a lambda, a comprehension, a keyword argument, a fresh-instance field, a list element, a star import) is patched at MODULE scope and the patch is ignored

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-B (cheap legs, emission vs battery-A byte-inert in all three, suite 3507/3525 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Second-order (carrier of #127's alias taint, which treats an ordinary call's result as a plain value; module-scope code is never lowered, so the weaver is the only fence).**

## MEASURED at HEAD `65237fdb` (each PROVES `plainlib.inc(3) == 4`; CPython runs `dec` and returns 2)
- `m = ident(plainlib); m.inc = plainlib.dec`
- `setattr(ident(plainlib), "inc", plainlib.dec)` (the literal is not a def of this file; the receiver is not a Name)
- `m = (lambda: plainlib)(); m.inc = ...`, `m = [x for x in [plainlib]][0]; m.inc = ...`, `m = ident(x=plainlib); m.inc = ...`
- order 2 past my own first draft (receiver ROOT a fresh instance / a literal): `m = H(plainlib); m.x.inc = ...`,
  `ms = [ident(plainlib)]; ms[0].inc = ...`; past the second (unbound names exempt, for pure_ast's
  `Constant.n = property(...)`): a LEADING `from aliaslib import *` exporting `pm`, then `pm.inc = ...`.
Fenced: the same shapes inside a function (Why3 type error / `_pyobj_state` frame); `__new__` returning a module (UB-7.6).

## REPAIR (Module3_Weaver.process, the #130-#135 block)
Keyed on the SINK, not on the alias spelling (a taint through call arguments was tried first and polluted five mirror
emissions — the alias set is file-wide by name): at MODULE and CLASS-BODY scope, an attribute store/delete or a
`setattr`/`delattr` is allowed only when the receiver IS a name whose every module-scope binding is a literal or a
call of a class defined in this module, or a name with no module-scope binding in a file without a star import.
CENSUS: module-scope attribute writes in the five trees are all direct stores on fresh instances (0746, 0772, 0774,
1101) or pure_ast's unbound `Constant`, plus witnesses already refused. Emission sweep: byte-inert in all three.
Witnesses 1378-1381.
