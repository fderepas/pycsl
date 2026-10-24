r"""Test 4404 -- gen #37 route #333 (control, expected PASS): control: a single underscore-prefixed user exception `_Private` with no twin (its stripped tag `Private` is unique) is NOT a collision. PROVED.
"""
# pycsl-expected: PASS
class _Private(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 2
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _Private()
    except _Private:
        return 2
    return 0

if __name__ == "__main__":
    assert g(0) == 2, g(0)
