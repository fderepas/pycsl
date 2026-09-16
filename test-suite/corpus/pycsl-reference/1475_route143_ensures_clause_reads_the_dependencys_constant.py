r"""Test 1475 - ROUTE #143 is not about `raises`: an ENSURES clause `\result == BASE` over the callee module's `BASE = -1`, with the importer binding `BASE = 5`, PROVED `caller() == 5` at HEAD while CPython returns -1 (gen #29). Refused: every clause of an injected contract is checked.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r143_enslib import base

BASE = 5


#@ ensures \result == 5
#@ assigns \nothing
def caller() -> int:
    return base()

