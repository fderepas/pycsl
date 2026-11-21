r"""Test 8085 -- routes #507 / #508 / #509 (control, expected PASS): a callee REACHED under the caller's `\all` binds `"ab" * n` to a local under its own `requires 0 <= n <= 1000`; CPython f(5) returns 1
"""
# pycsl-expected: PASS
#@ requires 0 <= n and n <= 1000
#@ ensures \result == 1
def g(n: int) -> int:
    t = "ab" * n
    v = {t}
    return 1


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print("result", f(5))
