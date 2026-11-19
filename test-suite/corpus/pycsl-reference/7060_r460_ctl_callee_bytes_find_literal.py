r"""Test 7060 -- route #460 (expected PASS): CONTROL -- the un-claimed `g` searches with an int LITERAL in 0..255 (`b.find(98)`), reached from `f` claiming `#@ no_exception \all`; PROVED at base and candidate.
"""
# pycsl-expected: PASS


def g(b: bytes) -> int:
    return b.find(98)


#@ no_exception \all
def f() -> int:
    return g(b"abc")


if __name__ == "__main__":
    print(f())
