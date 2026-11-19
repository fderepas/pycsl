r"""Test 7059 -- route #460 (expected FAIL): `b.find(n)` with an int `n` in an UN-claimed `g`, called by `f` claiming `#@ no_exception \all` (CPython ValueError for f(300): byte must be in range(0, 256)). PROVED at base 370db7dc2 (#452's front-end row read g's own claim); now REFUSED under g's reached claim.
"""
# pycsl-expected: FAIL


def g(b: bytes, n: int) -> int:
    return b.find(n)


#@ no_exception \all
def f(n: int) -> int:
    return g(b"abc", n)


if __name__ == "__main__":
    print("result", f(300))  # CPython: ValueError
