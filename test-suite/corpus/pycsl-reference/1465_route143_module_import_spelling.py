r"""Test 1465 - ROUTE #143 through a MODULE import (`import ... as lib; lib.f(k)`): PROVED at HEAD with the same folded `(5) < 0`; CPython raises. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r141_raiselib as lib

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return lib.f(k)

