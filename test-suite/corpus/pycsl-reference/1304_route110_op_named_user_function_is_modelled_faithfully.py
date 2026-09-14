"""Test 1304 — ROUTE #110 POSITIVE witness, and the file that BOUNDS the repair.

Byte-identical to 1303 except the postcondition is the TRUE one. The repair must not merely
stop the false proof — it must make the call FAITHFUL, so the callee's own `ensures` is
visible at the call site and `\result == x + 1` PROVES. Emitted:

    let xs = (let _alit = Array.make 1 ((any_1 x)) in _alit) in

WHY THIS FILE IS REQUIRED. 1303 asserts that something must NOT prove. A repair that
refused every such call, or left the argument unconstrained, would satisfy 1303 while
destroying the capability. Only a file that must STILL PROVE can fail when that happens.
"""
_ = 0  # anchor
#@ requires x0 >= 0
#@ ensures \result == x0 + 1
#@ assigns \nothing
def any_1(x0: int) -> int:
    return x0 + 1

#@ requires x >= 0
#@ ensures \result == x + 1
#@ assigns \nothing
def f(x: int) -> int:
    xs = [any_1(x)]
    return xs[0]
