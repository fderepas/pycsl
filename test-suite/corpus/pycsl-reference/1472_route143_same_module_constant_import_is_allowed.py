r"""Test 1472 - ROUTE #143 positive control (gen #29): the importer imports `LIM` FROM THE SAME MODULE as the callee, so the name denotes one binding; the tagged contract is ALLOWED and `requires k >= LIM` discharges at `g2(0)`. PASSES on both sides of the repair.
"""
_ = 0  # anchor
from multi_file_lib.r143_reqlib import g2, LIM


#@ ensures \result == 0
#@ assigns \nothing
def caller() -> int:
    return g2(0)
