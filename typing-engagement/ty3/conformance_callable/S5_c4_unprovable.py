from typing import Callable


# S5 C4 UNPROVABLE (the no-blend keystone, static half): a bare Callable gives
# NO value postcondition — `f` is an opaque function value. A postcondition
# asserting a specific value of `f(...)` (here `ensures \result == n + 1` where
# the body is `return f(n)`) is UNPROVABLE. This is the correct sound refusal:
# the static plane refuses a value theorem the function-type does not justify.
# A `\trusted` shortcut would blend the planes — refused.
#@ requires n >= 0
#@ ensures \result == n + 1
def apply_overpromise(f: Callable[[int], int], n: int) -> int:
    return f(n)
