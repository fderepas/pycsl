r"""Test 4497 -- gen #37 route #336 (expected FAIL): `xs: Sequence[float]`: the element was an `int`, `xs[0] % 1 == 0` PROVED; CPython False for [0.5]. Read as `List[float]` (identical emission); not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_sequence(xs: Sequence[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_sequence(*([0.5],)) == True, f_sequence(*([0.5],))
