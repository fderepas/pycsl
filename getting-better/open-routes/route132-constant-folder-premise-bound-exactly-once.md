# ROUTE #132 — the module/class CONSTANT FOLDERS take "bound exactly once" from the top-level single-name Assign statements only, and assume a folded collection is never mutated

**Status: CLOSED AND FULLY GATED by gen #25 (2026-09-15), battery-A (cheap legs, emission vs HEAD byte-inert in all three, suite 3503/3521 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. First-order (generator: witness-census — the coverage premise of `module_collect.collect_module_*` and `Module5._collect_class_constants`).**

## MEASURED at HEAD `65237fdb` (each PROVES, CPython contradicts)
Rebinding arm (`N = 3` folded to 3 while CPython reads 5): `N += 2`; `if True: N = 5`; `N, M = 5, 6`;
`for N in [5]: pass`; `setattr(sys.modules[__name__], "N", 5)` at module scope; `S = "a"; S += "b"`;
`LIMIT = 3; LIMIT += 10` used in `#@ requires x < LIMIT` (a legal CPython call violates the proved ensures);
class body `N = 3; N += 2` and `N = 3; if True: N = 5` read as `self.N`.
Mutation/alias arm (a str dict folded to its literal while CPython reads the mutated object):
`OP.update({...})` and `OP["a"] = "c"` at module scope; `d = OP; d["a"] = "c"` at module scope and INSIDE a
function (the store lowers as a no-op on an opaque int); order 2 past the first draft: `d, e = OP, 1`,
`for d in [OP]`, `L = [OP]; L[0]["a"] = "c"`.
Fenced: in-function `OP.pop`/`del OP[k]`/`NAMES.add` (mutating-call refusals), a non-literal module dict (not
folded, fresh `get` per read), a dependency's dict (not folded across modules), `self.N = 5` in a method (frame).

## REPAIR (Module3_Weaver.process)
For every module / class-body name bound by exactly one top-level single-name Assign/AnnAssign of a literal (the
folders' candidates) that is READ (a load, a `.N` load for a class, or a token of a `#@` line): refuse if it has any
other binding site in its scope, is named by a literal `setattr`/`delattr` on a module-like receiver, or — for a
mutable literal of a folded shape (a str-keyed dict, a str set, a list of tuples; a class-body str set) — if ANY
reference to it is not in a read position (a non-mutating method, a subscript load, `in`, an iteration, a pure
builtin argument, a binary operator), one alias level into a plain name allowed when that name is only read.
The first cut enumerated the alias spelling `x = OP` and was walked past three ways (generator #9: key on the object).
CENSUS: pycsl_lib json/encoder.py `ESCAPE_DCT.setdefault` (a genuine mutation of a folded dict); json/decoder.py
`BACKSLASH` as a default argument; no mirror or corpus site. Emission sweep on the draft: byte-inert in all three.
Witnesses 1367-1371; positive control 1373.
