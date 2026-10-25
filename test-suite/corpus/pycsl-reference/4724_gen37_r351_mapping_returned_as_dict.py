r"""Test 4724 -- gen #37 route #351 (expected FAIL): a `Mapping[str, int]` returned as `Dict[str, int]` PROVED, a verified store into it PROVED (CPython: mappingproxy TypeError). REFUSED now (route #351).
"""
# pycsl-expected: FAIL
from typing import Mapping, Dict

#@ ensures \result == d
def as_dict(d: Mapping[str, int]) -> Dict[str, int]:
    return d

#@ no_exception \all
#@ ensures \result == 5
def poke(e: Dict[str, int]) -> int:
    e["a"] = 5
    return e["a"]

if __name__ == "__main__":
    import types
    print(poke(as_dict(types.MappingProxyType({"a": 1}))))
