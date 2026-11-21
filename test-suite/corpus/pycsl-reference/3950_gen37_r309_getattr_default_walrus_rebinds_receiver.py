r"""Test 3950 -- gen #37 route #309 (expected FAIL): a walrus in a getattr default rebinds the receiver AFTER Python read it (`getattr(a, "n", z((a := K(7))))` reads the OLD a); sequencing the default first would read the new one, so it is REFUSED.
"""
# pycsl-expected: FAIL
class K:
    def __init__(self, v: int) -> None:
        self.n = v

#@ ensures \result == 0
def z(k: K) -> int:
    return 0

#@ ensures \result == 7
def f() -> int:
    a = K(4)
    y = getattr(a, "n", z((a := K(7))))
    return y

if __name__ == "__main__":
    assert f() == 7
