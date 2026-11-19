r"""Test 8902 -- lvC warnings.warn (expected FAIL): `warnings.warn` RAISES under a warnings filter set to
"error" (`python -W error`, `warnings.simplefilter("error")`: `UserWarning` propagates). It stays an
opaque call with no model (lvC added no warn model: the converted leaves claim only type safety + frame,
never `no_exception`), so a `#@ no_exception \all` claim over it must NOT be proved.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import warnings


#@ ensures \result == n
#@ assigns \nothing
#@ no_exception \all
def warn_always(n: int) -> int:
    warnings.warn("always")
    return n


if __name__ == "__main__":
    warnings.simplefilter("error")
    try:
        print("result", warn_always(7))
    except UserWarning as e:
        print("VIOLATION no_exception (UserWarning)", e)
