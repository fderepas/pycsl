r"""Test 4503 -- gen #37 route #336 (expected FAIL): `d: Mapping[str, float]`: value read as `int`, `d["a"] % 1 == 0` PROVED; CPython False. Read as `Dict[str, float]`, whose float value is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_mapping(d: Mapping[str, float]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_mapping(*({'a': 0.5},)) == True, f_mapping(*({'a': 0.5},))
