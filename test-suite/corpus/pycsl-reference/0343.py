"""Test 0343 — PyCSL Annotation Reference §3.1.18: Boolean atom `True`.

The `True` literal is the recommended form for vacuous preconditions
and postconditions, replacing the older `1 == 1` idiom. Module2's
grammar accepts it directly (`true_lit -> CSLBool(True)`), Module5
emits `{"type": "Bool", "value": True}` in the IR, and Module6
emits `true` (in spec context) or `1` (in body context) per
the int-bool duality. Why3 + Alt-Ergo discharge `True`-shaped
postconditions trivially.

This test confirms the end-to-end pipeline under full proof mode.
"""
#@ requires True
#@ ensures True
#@ assigns \nothing
def trivially_true(x: int) -> int:
    return x

if __name__ == "__main__":
    assert trivially_true(7) == 7
    assert trivially_true(0) == 0
    assert trivially_true(-3) == -3
    print("PASS")
