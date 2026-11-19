r"""Test 4327 -- gen #37 route #329 (control, expected PASS): control: `7 if not (x is not x) else 0` — identity is reflexive, the same-variable exemption holds under `not` and in an if-expression. PROVED.
"""
# pycsl-expected: PASS
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    x = 3
    return 7 if not (x is not x) else 0

if __name__ == "__main__":
    assert g() == 7, g()
