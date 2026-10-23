r"""Test 1470 - ROUTE #143 carrier-rerun (gen #29): `LIM` reaches the importer only through ANOTHER module's wildcard import (fail-closed at HEAD by the proof). Refused: the wildcard source's own module-level bindings are read.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_other import *
from multi_file_lib.r141_raiselib import f


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)

