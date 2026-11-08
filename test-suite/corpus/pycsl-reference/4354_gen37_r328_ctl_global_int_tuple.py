r"""Test 4354 -- gen #37 route #328 (expected PASS): control: `A, B = 1, 2` at module level pairs each target with an int, so `B % 1 == 0 and A * 0 == 0` PROVES.
"""
# pycsl-expected: PASS
A, B = 1, 2
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return B % 1 == 0 and A * 0 == 0

if __name__ == "__main__":
    assert g() == True
