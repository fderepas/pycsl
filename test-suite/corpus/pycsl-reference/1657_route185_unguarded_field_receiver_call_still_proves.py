r"""Test 1657 - ROUTE #185 control (gen #29): a field-receiver call to a method with NO precondition and NO escaping exception stays a plain stubbed call - the caller's claim about its own value still proves. (The callee's `ensures` does not reach a field receiver either way; that is not what #185 changed.)
"""
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ ensures \result == 1
    def one(self) -> int:
        return 1


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ ensures \result == 5
    def run(self) -> int:
        self.inner.one()
        return 5
