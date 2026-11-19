r"""Test 4401 -- gen #37 route #333 (expected FAIL): user classes `E` / `_E` merge into one WhyML `exception E`; `raise _E()` caught by `except E` PROVED `\result == 1` (CPython 2). REFUSED (PYCSL-R327-IDENT-COLLISION, route #333).
"""
# pycsl-expected: FAIL
class E(Exception):
    pass

class _E(Exception):
    pass

#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _E()
    except E:
        return 1
    except _E:
        return 2
    return 0

if __name__ == "__main__":
    assert g(0) == 1, g(0)
