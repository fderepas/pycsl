from typing import Callable


# S5 RESULT-REJECT (C3): f returns int; declaring -> str makes the body
# `return f(0)` a static WhyML type error ("int, expected string"). The result-
# type obligation is discharged by Why3's typecheck.
def apply_ret(f: Callable[[int], int]) -> str:
    return f(0)
