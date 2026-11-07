r"""Test 1476 - ROUTE #143 positive control (gen #29, carrier-rerun on draft 4): the importer and the callee's module each import `LIM` from the SAME constants module, so it is one binding. Draft 4 REFUSED this (it accepted only an import of the name from the callee's own file); the same-source rule now allows it and `requires k >= LIM` discharges at `g5(0)`. PASSES at HEAD and on the repair.
"""
_ = 0  # anchor
from multi_file_lib.r143_consts import LIM
from multi_file_lib.r143_viaconsts import g5


#@ ensures \result == 0
#@ assigns \nothing
def caller() -> int:
    return g5(0)

