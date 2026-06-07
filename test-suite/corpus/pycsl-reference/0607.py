"""Test 0607 — faithful local array-of-tuples: build, index, destructure (07-0903 W1).

A list of uniform fixed-arity tuples (`a = [(10, 20), (30, 40)]`, the directory/(key,value)
shape) lowers to a real `array (int, int)` — each element a Why3 tuple, NOT collapsed to one int
(the unsound behaviour W1 replaces). `a[i]` reads the element tuple (`Array.get`); `a[i][k]`
destructures its k-th component (`let (_r0, _) = a[i] in _r0`), distinct from a 2-D matrix access.
Bounds and `len` work as for any array. Previously this construct was hard-rejected (0442 C3).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 10
#@ assigns \nothing
def first_first() -> int:
    a = [(10, 20), (30, 40)]
    return a[0][0]


#@ requires 0 <= i and i < 2
#@ ensures \result >= 0
#@ assigns \nothing
def at_second(i: int) -> int:
    a = [(10, 20), (30, 40)]
    if a[i][0] >= 0:
        return a[i][1]
    return 0
