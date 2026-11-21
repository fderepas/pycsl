r"""Test 9128 -- run #5 lvJ str actual into an Optional[str] formal (expected PASS): a `str` argument to a
sibling method whose parameter is `Optional[str]` is the union's string arm (base: a bare string against the union, L3-tc failure).
"""
# pycsl-expected: PASS
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

    #@ ensures \result == "none" or \result == "some"
    #@ assigns \nothing
    def use(self, s: str) -> str:
        return self.tag(s)

if __name__ == "__main__":
    print(Namer().use("a"))
