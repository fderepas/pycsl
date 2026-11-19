r"""Test 3946 -- gen #37 route #309 (expected FAIL): `getattr(k, nm, 0)` on a known record: a non-literal name was classified ABSENT and answered the default; now an opaque per-site read.
"""
# pycsl-expected: FAIL
class K:
    def __init__(self, v: int) -> None:
        self.n = v

#@ ensures \result == 0
def f(k: K, nm: str) -> int:
    return getattr(k, nm, 0)

if __name__ == "__main__":
    assert f(K(4), "n") == 0
