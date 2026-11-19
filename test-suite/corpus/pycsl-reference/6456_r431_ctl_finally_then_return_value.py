r"""Test 6456 -- route #431 (expected PASS): CONTROL: an `-> int` function whose `finally:` block updates a local without jumping, with the `return` moved after the `try` statement (PYCSL-R431's advice); a `return` inside the TRY body of a `try` with a jump-free `finally` stays route #156's business. PROVED at base and candidate.
"""
# pycsl-expected: PASS


#@ requires x >= 0
#@ ensures \result == x + 2
def f(x: int) -> int:
    r = x
    try:
        r = r + 1
    finally:
        r = r + 1
    return r


if __name__ == "__main__":
    print(f(3))
