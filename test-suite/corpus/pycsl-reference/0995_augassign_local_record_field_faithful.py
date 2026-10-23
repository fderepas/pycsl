"""Test 0995 — the POSITIVE half of ROUTE #23(b): `p.f op= v` on a record-typed local now
proves the TRUE postcondition.

`0994` is this body with the FALSE `#@ ensures \result == 0`, which used to prove and now
correctly fails. This file carries the TRUE `#@ ensures \result == 5` and PROVES — which
nothing could do before, because the augmented store produced no IR at all and the model
kept the field at its constructed value.

Stating both halves is the point: a fix that merely REFUSED `p.f op= v` would make 0994
fail too, and no test could tell that apart from a faithful lowering. Only this file
distinguishes them.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class E:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0


#@ requires True
#@ ensures \result == 5
def bump() -> int:
    e = E()
    e.v += 5
    return e.v


if __name__ == "__main__":
    print(bump())
