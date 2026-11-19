r"""Test 4356 -- gen #37 route #328 (expected PASS): control: `a, b = 1, F` taints only `b` (component-precise), so `a % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
F = 0.5
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    a, b = 1, F
    return a % 1 == 0

if __name__ == "__main__":
    assert g() == True
