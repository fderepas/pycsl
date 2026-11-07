r"""Test 4362 -- gen #37 route #331 (expected PASS): control: an Optional field compares `==` to None and to itself (equality only, no arithmetic): PROVES.
"""
# pycsl-expected: PASS
from typing import Optional
class C:
    def __init__(self) -> None:
        self.r: Optional[int] = None

#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    c = C()
    return c.r == None and c.r == c.r

if __name__ == "__main__":
    assert g() == True
