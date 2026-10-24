r"""Test 4517 -- gen #37 route #336 (expected FAIL): `d: Dict[str, float]`: value read as `int`, `d["a"] % 1 == 0` PROVED; CPython False for {"a": 0.5}. The float value is erased; not provable.
"""
# pycsl-expected: FAIL
from typing import Dict, List, Set, Optional, Tuple
#@ ensures \result == True
def f_dict(d: Dict[str, float]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

if __name__ == "__main__":
    assert f_dict({"a": 0.5}) == True
