from typing import Callable


# S5 ARG-REJECT (C2): f expects an int argument; calling f(s) with s: str is a
# static WhyML type error ("string, expected int"). The arg-type obligation is
# discharged by Why3's typecheck — NOT by a runtime check.
def apply_str(f: Callable[[int], int], s: str) -> int:
    return f(s)
