r"""Test 1702 - ROUTE #202 control (gen #30): the refusal is gated on the callee's contract MENTIONING the parameter, because that is the only way a nameable hash can decide anything. An un-annotated parameter whose contract never reads it is the emitter's own plumbing shape - all 46 sites the #200 census found are of this kind - and it must keep working. Without this control the #202 fix could have been the blunt one, refusing every string literal at every erased parameter, and it would have taken the mirror's own emission with it. NOTE the callee's contract fixes `\\result` and NEVER mentions `p` - which is the whole point: a parameter no contract reads cannot decide anything, whatever the model substitutes for it.
"""
# pycsl-expected: PASS

_ = 0  # anchor


#@ requires True
#@ ensures \result == 7
def callee(p) -> int:
    return 7


#@ ensures \result == 7
def probe() -> int:
    return callee("a")
