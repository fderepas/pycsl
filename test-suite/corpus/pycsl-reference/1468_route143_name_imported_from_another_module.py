r"""Test 1468 - ROUTE #143 carrier-rerun (gen #29): the importer's `LIM` is not its own assignment but an import FROM ANOTHER MODULE (`LIM = 5` there). PROVED at HEAD; CPython raises. Refused: only an import of the SAME name from the SAME module is the same binding.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f
from multi_file_lib.r143_other import LIM


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)

