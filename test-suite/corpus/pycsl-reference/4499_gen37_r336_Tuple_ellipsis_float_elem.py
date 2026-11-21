r"""Test 4499 -- gen #37 route #336 (expected FAIL): `xs: Tuple[float, ...]`: element read as `int`, PROVED; CPython False for (0.5,). Read as `List[float]`; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_tuple_var(xs: Tuple[float, ...]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_tuple_var(*((0.5,),)) == True, f_tuple_var(*((0.5,),))
