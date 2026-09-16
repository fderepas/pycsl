r"""Test 1471 - ROUTE #143 carrier-rerun (gen #29): the callee's condition CALLS its module's helper `lim()` and the importer defines its own `lim` (fail-closed at HEAD by a Why3 error). Refused: callee names count, not only variables.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_fnlib import g


#@ ensures \result == 1
def lim() -> int:
    return 1


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return g(k)

