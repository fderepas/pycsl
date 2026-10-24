r"""Test 4349 -- gen #37 route #330 (expected FAIL): under `--strict-bare-containers`: an element of `xs: list` used as an int (`xs[0] * 0 == 0`) is REFUSED now (PYCSL-R325-OPAQUE-INT-FALLBACK).
"""
# pycsl-flags: --strict-bare-containers
# pycsl-expected: FAIL
#@ requires len(xs) >= 1
#@ ensures \result == True
#@ assigns \nothing
def g(xs: list) -> bool:
    return xs[0] * 0 == 0

if __name__ == "__main__":
    assert g(["a"]) == True
