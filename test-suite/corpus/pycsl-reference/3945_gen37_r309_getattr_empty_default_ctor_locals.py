r"""Test 3945 -- gen #37 route #309 (expected FAIL): `getattr(a, "n", {}) - getattr(b, "n", {})` on constructor locals: one shared constant proved 0; now the field reads.
"""
# pycsl-expected: FAIL
class K:
    def __init__(self, v: int) -> None:
        self.n = v

#@ ensures \result == 0
def f() -> int:
    a = K(4)
    b = K(5)
    return getattr(a, "n", {}) - getattr(b, "n", {})

if __name__ == "__main__":
    assert f() == 0
