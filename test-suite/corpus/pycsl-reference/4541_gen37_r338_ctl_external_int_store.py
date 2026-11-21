r"""Test 4541 -- gen #37 route #338: CONTROL: external stores of provably-int values (`c.r = 7`, `setattr(c, "r", 3)`) keep the field int; `c.r % 1 == 0` PROVES (CPython True).
"""
class C:
    def __init__(self) -> None:
        self.r = 0

#@ ensures \result == True
def g(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    c = C()
    c.r = 7
    setattr(c, "r", 3)
    assert g(c) == True
