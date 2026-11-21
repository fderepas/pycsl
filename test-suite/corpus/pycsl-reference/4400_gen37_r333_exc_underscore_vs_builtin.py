r"""Test 4400 -- gen #37 route #333 (expected FAIL): user `class _ValueError(Exception)` raised, `except ValueError: return 1` under `no_exception \all`: safe_exc_name stripped the `_`, the WhyML tag merged with the builtin and PROVED no exception (CPython propagates). REFUSED (PYCSL-R327-IDENT-COLLISION, route #333).
"""
# pycsl-expected: FAIL
class _ValueError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _ValueError()
    except ValueError:
        return 1
    return 0

if __name__ == "__main__":
    assert g(0) == 1, g(0)
