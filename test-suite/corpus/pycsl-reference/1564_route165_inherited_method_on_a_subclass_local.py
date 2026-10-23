r"""Test 1564 - ROUTE #165 (gen #29): the invariant-carrying method is INHERITED and the receiver is a SUBCLASS local; `d.x = -5; d.get() >= 0` PROVED at HEAD; CPython -5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


class D(C):
    pass


#@ ensures \result >= 0
def probe() -> int:
    d = D()
    d.x = -5
    return d.get()

