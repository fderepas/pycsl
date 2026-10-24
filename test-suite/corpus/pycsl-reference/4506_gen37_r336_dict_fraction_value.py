r"""Test 4506 -- gen #37 route #336 (expected FAIL): `d: Dict[str, Fraction]`: value read as `int`, PROVED; CPython False for Fraction(1, 2). The value is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_dict_fraction(d: Dict[str, Fraction]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_dict_fraction(*({'a': Fraction(1, 2)},)) == True, f_dict_fraction(*({'a': Fraction(1, 2)},))
