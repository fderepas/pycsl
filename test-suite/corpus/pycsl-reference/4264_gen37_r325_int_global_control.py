r"""Test 4264 -- gen #37 route #325 control (expected PASS): module-level INT bindings (`K = 5`, `N = K * 2 + 1`) keep their int model.
"""
# pycsl-expected: PASS
K = 5
N = K * 2 + 1
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if N % 1 == 0 and K * 0 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
