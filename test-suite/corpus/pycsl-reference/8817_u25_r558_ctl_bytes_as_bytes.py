r"""Test 8817 -- route #558 (control, expected PASS): `bytearray(n)` used as bytes -- a byte read of a fresh buffer -- never stored into a str / number container; CPython 0
"""
# pycsl-expected: PASS


#@ no_exception \all
#@ ensures \result == 0
def g(k: int) -> int:
    b = bytearray(4)
    return b[0]


if __name__ == "__main__":
    print(g(1))
