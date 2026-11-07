r"""Test 1469 - ROUTE #143 carrier-rerun (gen #29): the clashing binding sits inside a module-level `if` (fail-closed at HEAD by the proof). Refused by the module-scope binding walk, which descends compound statements.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f
if True:
    LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)

