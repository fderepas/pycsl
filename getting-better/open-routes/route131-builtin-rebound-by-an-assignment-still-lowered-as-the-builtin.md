# ROUTE #131 — a BUILTIN rebound by an assignment is still lowered as the builtin

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-A (cheap legs, emission vs HEAD byte-inert in all three, suite 3503/3521 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. First-order (the `def len` / `import abs` / star `abs` spellings were measured faithful by gen #24; the assignment spelling was never probed).**

## MEASURED at HEAD `65237fdb`
- module `len = sum`, `f(): xs = [5]; return len(xs)` with `\result == 1` PROVES; CPython 5.
- local `len = sum` inside `f`: PROVES `== 1`; CPython 5.
- module `for max in [min]: pass`, `max(2, 5) == 5` PROVES; CPython 2.
- order 2, carriers of my own drafts: `exec("len = sum")` (a constant exec is spliced AFTER the weaver's checks);
  `from builtins import sum as len`; `ValueError = KeyError` with `raise ValueError` / `except KeyError` (the model
  raises past the handler and `raises { ValueError }` makes the ensures vacuous, CPython returns 2); an unannotated
  PARAMETER `def f(len, xs): return len(xs)` (`f(sum, [5]) == 1` proved).
Fenced: a Callable parameter named `len` (ir-emit refusal), `for len in [sum]` inside a function (type error),
`abs = plainlib.dec` (the call lowers opaque).

## REPAIR (Module3_Weaver.process)
A name of the builtins namespace (every public name of `builtins`) bound by a store (assignment, augmented/annotated,
for/with target, walrus, except-as, match capture) or a PARAMETER, in a module or function scope where it is READ, is
refused; `from builtins import a as b` renaming is refused; a constant `exec` whose text names a builtin, an imported
name or a folded constant is refused. The first cut keyed on CALLS of a short list and was walked past three times.
CENSUS: 0 sites except pycsl_lib json/encoder.py `_make_iterencode(..., isinstance=isinstance, ...)` (not ingested).
Witnesses 1365, 1366, 1374, 1375, 1376.
