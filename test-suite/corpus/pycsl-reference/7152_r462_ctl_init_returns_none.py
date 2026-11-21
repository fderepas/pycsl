r"""Test 7152 -- route #462 (expected PASS): CONTROL -- `__init__` bodies that return nothing (a bare `return` on one path, `return None` on another, a nested helper `def` that returns a value) and a claimed caller that constructs the class; CPython raises nothing. PROVED at base and candidate.
"""
# pycsl-expected: PASS


class C:
    def __init__(self, n: int) -> None:
        self.n = n
        if n < 0:
            return
        return None


#@ requires n >= 0
#@ ensures \result == n
#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return n


if __name__ == "__main__":
    print(f(1))
