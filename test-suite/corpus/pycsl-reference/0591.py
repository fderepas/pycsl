"""Test 0591 — negative: imported constant is bound to its TRUE value (1111-spec R6).

Same call as `0590`, but the postcondition over-claims `\result == 1`. Since `clamp_seek`
returns `how` and `how == SEEK_SET` folds to `0`, the VC refutes `\result == 1`. Confirms the
imported constant carries its real literal value (`0`), not a free `val constant` about which
`1` would be equally (un)knowable.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from multi_file_lib.r1111_stub import clamp_seek, SEEK_SET


#@ ensures \result == 1
#@ assigns \nothing
def run() -> int:
    return clamp_seek("f", SEEK_SET)
