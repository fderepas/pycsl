"""Test 0298 — PyCSL Annotation Reference 11.2 — Ghost string \str_length and \str_sub"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def test_str_builtins(n: int) -> int:
    #@ ghost s : string = "hello"
    #@ ghost slen = \str_length(s)
    #@ ghost sub = \str_sub(s, 0, 3)
    return n
