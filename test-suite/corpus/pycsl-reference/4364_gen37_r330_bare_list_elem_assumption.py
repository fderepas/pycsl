r"""Test 4364 -- gen #37 route #330 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION BARE-CONTAINER-INT): `xs: list` is `array int`, so `xs[0] * 0 == 0` PROVES although CPython refutes it for `["a"]`. Twin 4349 drops it.
"""
# pycsl-expected: PASS
#@ requires len(xs) >= 1
#@ ensures \result == True
#@ assigns \nothing
def g(xs: list) -> bool:
    return xs[0] * 0 == 0

if __name__ == "__main__":
    assert g(["a"]) == True
