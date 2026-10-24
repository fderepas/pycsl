r"""Test 4427 -- gen #37 route #334 (expected FAIL): under `--strict-bare-containers` (BARE-CONTAINER-INT dropped, now covering a bare `dict`): a value of `d: dict` is of unknown type, so `d["a"] % 1 == 0` is REFUSED (PYCSL-R325-OPAQUE-INT-FALLBACK); it PROVED before (CPython False for {"a": 0.5}).
"""
# pycsl-flags: --strict-bare-containers
# pycsl-expected: FAIL
from typing import List, Dict, Sequence
#@ ensures \result == True
#@ assigns \nothing
def g(d: dict) -> bool:
    if "a" not in d:
        return True
    return d["a"] % 1 == 0

if __name__ == "__main__":
    assert g({"a": 0.5}) == True, g({"a": 0.5})
