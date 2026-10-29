r"""Test 6980 -- route #449 (expected PASS): CONTROL: calls of module functions that BIND (a default left out and given by keyword, a keyword-only parameter, a positional-only parameter by position, `*args` / `**kwargs` formals absorbing surplus), each callee with an `ensures`, the caller under `#@ no_exception \all`. Admitted; PROVED at base and candidate (CPython ok).
"""
# pycsl-expected: PASS
#@ ensures \result == a + b
def add(a: int, b: int = 1) -> int:
    return a + b


#@ ensures \result == a - k
def sub(a: int, *, k: int = 0) -> int:
    return a - k


#@ ensures \result == a
def ident(a: int, /) -> int:
    return a


#@ no_exception \all
#@ ensures \result == 3 * n + 3
def f(n: int) -> int:
    return add(n) + add(n, b=2) + add(a=n) + sub(n) + sub(n, k=0) - ident(n)


if __name__ == "__main__":
    print(f(2))
