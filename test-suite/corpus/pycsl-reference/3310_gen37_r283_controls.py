r"""Test 3310 -- route #283 CONTROLS (expected PASS): a list returned by a call whose arguments hold
no list (`ident([5])`), a read-only binding of a returned alias, a FRESH copy (`sorted(a)`)
mutated afterwards, and an ordinary annotated local are faithful and must keep proving after the
repair (none is refused).
"""
# pycsl-expected: PASS
from typing import List


#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x


#@ ensures \result == 2
#@ assigns \nothing
def fresh_from_literal_arg() -> int:
    b: List[int] = ident([5])
    b.append(9)
    return len(b)


#@ ensures \result == 1
#@ assigns \nothing
def read_only_alias() -> int:
    a: List[int] = [0]
    b: List[int] = ident(a)
    return len(b)


#@ ensures \result == 1
#@ assigns \nothing
def sorted_copy_mutated() -> int:
    a: List[int] = [0]
    b: List[int] = sorted(a)
    b.append(1)
    return len(a)


#@ ensures \result == 2
#@ assigns \nothing
def plain_local() -> int:
    b: List[int] = [5]
    b.append(9)
    return len(b)


if __name__ == "__main__":
    assert fresh_from_literal_arg() == 2
    assert read_only_alias() == 1
    assert sorted_copy_mutated() == 1
    assert plain_local() == 2
