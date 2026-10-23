r"""Test 1466 - ROUTE #143 through a WILDCARD import that the importer REBINDS afterwards (`from lib import *; LIM = 5`): PROVED at HEAD; CPython raises (the callee still reads its own module's -1). Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r141_raiselib import *

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)

