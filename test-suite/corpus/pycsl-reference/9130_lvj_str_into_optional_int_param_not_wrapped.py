r"""Test 9130 -- run #5 lvJ str actual into an Optional[str] formal (expected FAIL): CONTROL: a `str` argument to an
`Optional[int]` formal is NOT wrapped into the union (its arm carries an int): the emission stays ill-typed (fail-closed).
"""
# pycsl-expected: FAIL
from typing import Optional

def mutable_state(cls):
    return cls

@mutable_state
class Namer:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == 7
    #@ assigns \nothing
    def tag(self, x: Optional[int]) -> int:
        if x is None:
            return 7
        return 7

    #@ ensures \result == 7
    #@ assigns \nothing
    def use(self, s: str) -> int:
        return self.tag(s)

if __name__ == "__main__":
    print(Namer().use("a"))
