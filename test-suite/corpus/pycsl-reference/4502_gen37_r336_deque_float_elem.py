r"""Test 4502 -- gen #37 route #336 (expected FAIL): `xs: Deque[float]`: element read as `int`, PROVED; CPython False for deque([0.5]). Erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_deque(xs: Deque[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_deque(*(deque([0.5]),)) == True, f_deque(*(deque([0.5]),))
