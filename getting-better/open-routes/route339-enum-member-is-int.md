# OPEN ROUTE #339 — ENUM MEMBERS ARE MODELLED AS PLAIN INTS (arithmetic/ordering on plain Enum; user __eq__/__lt__ ignored)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r339/`: `C.A` lowers to `get_A _class_c : int` and #325 classes it int (int-literal value). Plain Enum: `x - x`, `x < x`, `-x + x`,
`x * x`, `a[x]` raise TypeError in CPython but `no_exception \all` + value claims prove (d26, d27, d31, e12, e13, e14). User `__eq__`/`__lt__` on Enum/IntEnum
are emitted but ignored: `x == x` proves True while CPython's __eq__ returns False (d17, d18, d19). Not BUILTIN-EXACT (static type is the user class).
Repair: Enum members are opaque values of an abstract per-enum type (no int arithmetic/ordering for plain Enum; IntEnum/IntFlag members may
keep int semantics only when no user dunder overrides the operator); operators on enum members dispatch to user dunders or are refused.
