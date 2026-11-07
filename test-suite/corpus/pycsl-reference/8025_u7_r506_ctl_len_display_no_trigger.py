r"""Test 8025 -- route #506 (control, expected PASS): `len([n, n + 1])` under `#@ no_exception \all` -- a display modelled by its size holds no trigger-shaped element, so nothing is refused; CPython g(5) returns 7)
"""
# pycsl-expected: PASS

#@ no_exception \all
#@ ensures \result == n + 2
def g(n: int) -> int:
    y = len([n, n + 1])
    return y + n


if __name__ == "__main__":
    print("result", g(5))
