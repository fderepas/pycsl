r"""Test 9129 -- run #5 lvJ str actual into an Optional[str] formal (expected FAIL): the 9128 program with the FALSE claim
that the call answers "none" (`Namer().use("a")` returns "some").
"""
# pycsl-expected: FAIL
from typing import Optional

def mutable_state(cls):
    return cls

@mutable_state
class Namer:
    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result == "none" or \result == "some"
    #@ assigns \nothing
    def tag(self, x: Optional[str]) -> str:
        if x is None:
            return "none"
        return "some"

    #@ ensures \result == "none"
    #@ assigns \nothing
    def use(self, s: str) -> str:
        return self.tag(s)

if __name__ == "__main__":
    print(Namer().use("a"))
