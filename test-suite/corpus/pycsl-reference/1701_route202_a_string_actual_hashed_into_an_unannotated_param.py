r"""Test 1701 - ROUTE #202 carrier (gen #30): the residue route #200 left. #200 refuses a string literal actual against a parameter DECLARED `int`/`bool`/`float`, and its repair note says why the DECLARED key was chosen: the 46 sites where a string literal reaches an `int` param across the 53 mirror emissions are `int` BY ERASURE. That is exactly the hole - a parameter with NO annotation is erased to `int` by the emitter and gets the SAME `stable_hash` substitution. This emitted `(callee 747471683)` and PROVED `\result == 1` while CPython answers 2 (`"a" == 747471683` is False); the TRUE twin was REFUSED. Now refused too, gated on the condition that actually matters: the callee's own contract MENTIONS the parameter, which is what makes a nameable hash decidable. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


#@ requires True
#@ ensures p == 747471683 ==> \result == 1
#@ ensures p != 747471683 ==> \result == 2
def callee(p) -> int:
    if p == 747471683:
        return 1
    return 2


#@ ensures \result == 1
def probe() -> int:
    return callee("a")
