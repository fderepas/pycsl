"""Test 0592 — negative: omitting a NON-defaulted required arg is a hard error (1111-spec R7).

`clamp_seek(name, how, mode=7)` has no default for `how`. Calling `clamp_seek("f")` omits
`how`, which has no default — PyCSL MUST raise a descriptive arity error rather than emit a
silent partial application. (Contrast `0590`, where the omitted arg is the defaulted `mode`.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from multi_file_lib.r1111_stub import clamp_seek


#@ assigns \nothing
def run() -> int:
    return clamp_seek("f")
