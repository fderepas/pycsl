r"""Test 1573 - ROUTE #167 control (gen #29): a stubbed call to a method with NO precondition is untouched - its result-only postcondition still reaches the caller - and the guarded method itself still proves.
"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x

    #@ ensures \result == 1
    def one(self) -> int:
        return 1


#@ ensures \result == 5
def probe() -> int:
    c = C(0)
    r = c.one()
    return r + 4
