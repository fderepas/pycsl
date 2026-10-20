r"""Test 3382 -- route #288 (expected PASS): CONTROLS: a FRESH-returning callee whose arguments hold no list (`make()`) stored through, and a read-only returned alias, keep PROVING after the repair.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \length(\result) == 2
#@ assigns \nothing
def make() -> List[int]:
    return [0, 0]


#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
#@ \trusted
def tid(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 5
def fresh_store() -> int:
    b = make()
    b[0] = 5
    return b[0]


#@ ensures \result == 2
def read_only_alias() -> int:
    a: List[int] = [1, 2]
    b = tid(a)
    return len(b)


if __name__ == "__main__":
    assert fresh_store() == 5
    assert read_only_alias() == 2
