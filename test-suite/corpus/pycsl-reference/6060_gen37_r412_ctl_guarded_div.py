r"""Test 6060 -- gen #37 route #412 (expected PASS): CONTROL: float `x / y` with `requires y != 0.0`, `1.0 / x` with `requires x > 0.0`, and int `a / b` with `requires b != 0` and a bounded `a`, under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires y != 0.0
#@ no_exception \all
def f(x: float, y: float) -> float:
    return x / y


#@ requires x > 0.0
#@ no_exception \all
def g(x: float) -> float:
    return 1.0 / x


#@ requires b != 0
#@ requires -1000 <= a and a <= 1000
#@ no_exception \all
def h(a: int, b: int) -> float:
    return a / b


if __name__ == "__main__":
    print(f(1.0, 2.0), g(4.0), h(1, 3))
