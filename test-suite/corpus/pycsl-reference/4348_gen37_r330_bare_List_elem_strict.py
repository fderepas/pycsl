r"""Test 4348 -- gen #37 route #330 (expected FAIL): under `--strict-bare-containers` (BARE-CONTAINER-INT dropped): an element of `xs: List` is of unknown type, so `xs[0] % 1 == 0` is REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-flags: --strict-bare-containers
# pycsl-expected: FAIL
from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List) -> bool:
    return xs[0] % 1 == 0

if __name__ == "__main__":
    assert g([0.5]) == True
