r"""Test 4508 -- gen #37 route #336 (expected FAIL): `d: D` with `D: TypeAlias = Dict[str, float]`: value read as `int`, PROVED; CPython False. Resolved; the float value is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_dict_alias(d: D) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_dict_alias(*({'a': 0.5},)) == True, f_dict_alias(*({'a': 0.5},))
