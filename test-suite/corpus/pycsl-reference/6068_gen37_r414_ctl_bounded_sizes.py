r"""Test 6068 -- gen #37 route #414 (expected PASS): CONTROL: `len(range(n))`, `range(a, b)`, `"ab" * n`, `[0] * n` and `1 << n` with `0 <= n <= 1000` (and `0 << m` for any `m >= 0`) under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
def f(n: int) -> int:
    return len(range(n))


#@ requires 0 <= a and a <= b and b <= 1000
#@ no_exception \all
def f2(a: int, b: int) -> int:
    return len(range(a, b))


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
def g(n: int) -> int:
    s = "ab" * n
    xs = [0] * n
    return 0


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
def h(n: int) -> int:
    return 1 << n


#@ requires m >= 0
#@ no_exception \all
def z(m: int) -> int:
    return 0 << m


if __name__ == "__main__":
    print(f(5), f2(1, 4), g(3), h(10), z(2**70))
