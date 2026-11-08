r"""Test 4516 -- gen #37 route #336 (expected FAIL): `d: Dict[str, Num]` (`Num: TypeAlias = float`): value read as `int`, PROVED; CPython False. Resolved; the float value is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Dict, TypeAlias
Num: TypeAlias = float
#@ ensures \result == True
def f(d: Dict[str, Num]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True
if __name__ == "__main__":
    assert f({"a": 0.5}) == True
