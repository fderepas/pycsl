from typing import Callable


# S5 PASS (C1/C2/C3): a Callable[[int], int]-typed parameter lowers to a
# function-type; the call `f(n)` type-checks (arg int matches, result int).
# The tautological `ensures \result == f(n)` mirrors the body and proves.
#@ requires n >= 0
#@ ensures \result == f(n)
def apply_fn(f: Callable[[int], int], n: int) -> int:
    return f(n)


if __name__ == "__main__":
    #@ requires x >= 0
    #@ ensures \result == x + 1
    def add_one(x: int) -> int:
        return x + 1

    r = apply_fn(add_one, 5)
    #@ assert r == 6
