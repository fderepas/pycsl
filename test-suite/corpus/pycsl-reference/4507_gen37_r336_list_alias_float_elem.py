r"""Test 4507 -- gen #37 route #336 (expected FAIL): `xs: Vec` with `Vec = List[float]`: element read as `int`, PROVED; CPython False. Resolved to `List[float]`; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_list_alias(xs: Vec) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_list_alias(*([0.5],)) == True, f_list_alias(*([0.5],))
