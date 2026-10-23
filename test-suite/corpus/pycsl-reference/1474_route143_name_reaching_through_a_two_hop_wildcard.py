r"""Test 1474 - ROUTE #143 carrier-rerun (gen #29): `LIM = 5` reaches the importer through a wildcard of a module that itself wildcard-imports it. Refused (fail-closed at HEAD by the proof).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_hop import *
from multi_file_lib.r141_raiselib import f


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)

