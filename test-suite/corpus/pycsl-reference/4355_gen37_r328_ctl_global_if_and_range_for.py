r"""Test 4355 -- gen #37 route #328 (expected PASS): control: `if True: K = 3` and `for I in range(3)` bind ints, so `K * 0 == 0 and I % 1 == 0` PROVES.
"""
# pycsl-expected: PASS
if True:
    K = 3
for I in range(3):
    pass
#@ ensures \result == True
#@ assigns \nothing
def g() -> bool:
    return K * 0 == 0 and I % 1 == 0

if __name__ == "__main__":
    assert g() == True
