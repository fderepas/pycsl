r"""Test 4498 -- gen #37 route #336 (expected FAIL): `xs: Collection[float]`: element read as `int`, `x % 1 == 0` PROVED; CPython False. Erased (no element model); not provable.
"""
# pycsl-expected: FAIL
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_collection(xs: Collection[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_collection(*([0.5],)) == True, f_collection(*([0.5],))
