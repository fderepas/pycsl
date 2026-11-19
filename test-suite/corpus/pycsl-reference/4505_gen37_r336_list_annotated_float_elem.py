r"""Test 4505 -- gen #37 route #336 (expected FAIL): `xs: List[Annotated[float, "u"]]`: element read as `int`, PROVED; CPython False. Read as `List[float]`; not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_list_annotated(xs: List[Annotated[float, "u"]]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_list_annotated(*([0.5],)) == True, f_list_annotated(*([0.5],))
