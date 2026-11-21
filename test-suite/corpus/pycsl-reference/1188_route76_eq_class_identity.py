"""1188 — ROUTE #76 NEGATIVE: `==` on a class instance is STRUCTURAL, Python's is IDENTITY.

PyCSL models a class instance as a Why3 RECORD, and Why3's logic `=` on a record is
equality of the FIELD VALUES. Python's `==` on a class that defines no `__eq__` is
`object.__eq__`, i.e. IDENTITY. `dup` returns a FRESH object, so CPython answers

    dup(a) == a   ->   False

(measured by RUNNING it, not reasoned about), while `ensures \\result == x` PROVED. That is
a FALSE POSTCONDITION about ordinary TOTAL Python — the #69 class: no `no_exception`, no
memory-model flag, no opt-in of any kind.

This is the DUAL of routes #42/#52, which found `is` decided by VALUE equality (`is` too
WEAK); this is `==` too STRONG. `is` got its own IR operator there, but the `==` side of
the same coin was never examined, and the spec grammar has no `is` at all — so there was
no identity machinery to reuse.

ANTI-VACUITY is carried by 1189: the TRUE twin about this same program FAILS, so the model
was not merely incomplete here. 1190 is the accessor POSITIVE control that the repair must
not break, and 1191 the `@dataclass` control where structural equality is CORRECT.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


class C:
    v: int

    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == x
#@ assigns \nothing
def dup(x: C) -> C:
    return C(x.v)
