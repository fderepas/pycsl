r"""Test 4267 -- gen #37 route #325 control (expected PASS): `random.randint` returns an int.
"""
# pycsl-expected: PASS
import random
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    r = random.randint(0, 5)
    if r % 1 == 0:
        return 1
    return 0

if __name__ == "__main__":
    assert g() == 1
