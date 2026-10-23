# ROUTE #133 — a def nested in a METHOD, named like a method of the class, replaces that method (body swapped, postcondition dropped)

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-A (cheap legs, emission vs HEAD byte-inert in all three, suite 3503/3521 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Second-order (carrier of #122's nested arm, whose collision count covers non-method defs only).**

## MEASURED at HEAD `65237fdb`
`class C: h(self) -> 1` with FALSE `#@ ensures \result == 2`, and `m(self): def h(): return 2; return 0`; `f() = C().h()`
with `\result == 2`: the whole file PROVES. Emission: `let c__h (self: c) = 2` WITHOUT the `result = 2`
postcondition, callers through `val c_h_0 ensures result = 2`. CPython `C().h()` returns 1. Control without the nested
def: refused on `c__h'vc`.
Fenced: a subclass method vs a nested def in a base method (the subclass body is checked); a nested def named like
a FOREIGN base's method (opaque; WATCH).

## REPAIR (Module3_Weaver.process)
A def nested (at any depth, not inside a nested class) in a method of class K whose name is a method of K or of an
in-module base of K is refused. CENSUS: 0 sites in the four trees. Witness 1372.
