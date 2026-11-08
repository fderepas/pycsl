r"""Test 4358 -- gen #37 route #330 (expected PASS): control: a string-encoding result is still EQUAL to itself (no NaN): `f"{n}" == f"{n}"` PROVES.
"""
# pycsl-expected: PASS
#@ ensures \result == True
#@ assigns \nothing
def g(n: int) -> bool:
    return f"{n}" == f"{n}"

if __name__ == "__main__":
    assert g(3) == True
