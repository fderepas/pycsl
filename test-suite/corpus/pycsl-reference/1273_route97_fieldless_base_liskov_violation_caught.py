# pycsl-flags: --check-behavioral-subtyping
# pycsl-expected: FAIL
"""1273 — (#49) ROUTE #97, THE EXPLOIT ARM. A Liskov violation behind a FIELDLESS base.

`Sub.f` overrides `Base.f` and STRENGTHENS its precondition (`x >= 5` vs `x >= 0`) —
byte-for-byte the violation corpus file 0445 exists to reject. The ONLY difference from
0445 is that `Base` declares no instance field.

AT HEAD a32ec69e THIS FILE REPORTED `Verification SUCCESS! All contracts formally
proven.` and emitted ZERO refinement goals: a class becomes a record `type_decl` only
`if fields or bases:`, so a stateless base is absent from `records` in
`ir_resolve.apply_inheritance`, whose `if base is None: continue` skipped the ONLY place
the Liskov override pair is ever recorded. The cleaner the base class, the less checking
it received.

After the repair the goal `sub__f_refines_base` is emitted and is UNPROVABLE
(`(x >= 0 -> x >= 5)` is false), so the file MUST FAIL. If this ever proves again, the
obligation has been dropped a second time.
"""


class Base:
    #@ requires x >= 0
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x


class Sub(Base):
    #@ requires x >= 5
    #@ ensures \result >= x
    #@ assigns \nothing
    def f(self, x: int) -> int:
        return x
