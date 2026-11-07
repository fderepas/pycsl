r"""Test 1919 — gen #33 (expected PASS): the CONTROL for 1918.

A str PARAM concatenated with a literal. This shape ALWAYS type-checked, and it emits no
`str_concat_op` at all — a different lowering entirely. It is the control that makes 1918
mean something: the `unbound … 'concat'` bug lived in the DIFFERENCE between the two shapes,
so a corpus containing only one of them could not see it, and for a long time did not.

Kept as a positive control so that a future repair which "fixes" 1918 by refusing string
concatenation, or by pulling `use string.String` unconditionally into every module, is caught
by something rather than by nobody.
"""
# pycsl-expected: PASS


#@ requires len(x) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def f(x: str) -> int:
    s = x + "b"
    return len(s)
