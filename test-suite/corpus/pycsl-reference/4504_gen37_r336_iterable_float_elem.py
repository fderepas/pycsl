r"""Test 4504 -- gen #37 route #336 (expected FAIL): `xs: Iterable[float]`: element read as `int`, PROVED; CPython False. Erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_iterable(xs: Iterable[float]) -> bool:
    for x in xs:
        if x % 1 != 0:
            return False
    return True

if __name__ == "__main__":
    assert f_iterable(*([0.5],)) == True, f_iterable(*([0.5],))
