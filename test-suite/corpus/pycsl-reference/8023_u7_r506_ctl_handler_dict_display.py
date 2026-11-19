r"""Test 8023 -- route #506 (control, expected PASS): inside a `try` whose handler catches ZeroDivisionError, the division is bound by a plain statement (`q = 10 // n`) before the dict display `{1: q}` (which this lowering models opaquely, `any_map`, so a division written INSIDE it would be refused): its obligation is asserted (route #171: the handler relies on it, discharged by `requires n > 0`) and nothing is refused; CPython f(5) returns 6
"""
# pycsl-expected: PASS


#@ requires n > 0
#@ ensures \result == n + 1
def f(n: int) -> int:
    try:
        q = 10 // n
        dd = {1: q}
        return n + 1
    except ZeroDivisionError:
        return 0


if __name__ == "__main__":
    print("result", f(5))
