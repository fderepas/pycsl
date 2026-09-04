"""Test 1001 — the POSITIVE half of ROUTE #28: a module-global field store is now MODELLED.

`1000` is this body with the FALSE `#@ ensures \result == 0`, which used to prove and now
correctly fails. This file carries the TRUE `#@ ensures \result == 7` and PROVES — which
nothing could do before, because the store produced no IR at all and the read returned the
global's initialiser.

Note the `#@ assigns g.v`. It is not decoration: the store is now a real write to a global
mutable record, so Why3's frame check requires it. A function that writes a module-global
field without declaring it is rejected — which is the sound direction, and the reason this
closes as a capability rather than as a refusal.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires g.v == 0
#@ assigns g.v
#@ ensures \result == 7
def f() -> int:
    g.v = 7
    return g.v


if __name__ == "__main__":
    print(f())
