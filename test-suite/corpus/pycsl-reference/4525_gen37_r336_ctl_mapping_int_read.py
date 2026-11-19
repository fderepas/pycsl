r"""Test 4525 -- gen #37 route #336 (expected PASS): CONTROL: a READ of `d: Mapping[str, int]` PROVES (read as `Dict[str, int]`).
"""
# pycsl-expected: PASS
from typing import Mapping

#@ ensures \result == True
def has(d: Mapping[str, int]) -> bool:
    if "a" in d:
        return d["a"] - d["a"] == 0
    return True

if __name__ == "__main__":
    assert has({"a": 3}) == True
