r"""Test 5460 -- gen #37 systematic rule S1 (expected PASS): CONTROL: a user exception deriving from the BUILTIN `ValueError` (a modelled base: builtin exception classes are in S1's BASE-MODEL table) raised and caught under `no_exception \all`; PROVED at base 7bf752d4e and after.
"""
# pycsl-expected: PASS
class BadValue(ValueError):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise BadValue("x")
    except BadValue:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1 and g(1) == 1
