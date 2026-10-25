r"""Test 5072 -- gen #37 route #375 (expected FAIL): NEW shape: `g(*self)` under `no_exception \all` (TypeError: argument after * must be an iterable). FAILS now.
"""
# pycsl-expected: FAIL
def g(*a: int) -> int:
    return 0

class W:
    #@ no_exception \all
    def m(self) -> int:
        return g(*self)

if __name__ == "__main__":
    print(W().m())
