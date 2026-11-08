r"""Test 3947 -- gen #37 route #309 (expected PASS): CONTROL: a record parameter's declared field with a call default proves `\result == k.n`.
"""
# pycsl-expected: PASS
class K:
    def __init__(self, v: int) -> None:
        self.n = v

def z() -> int:
    return 0

#@ ensures \result == k.n
def f(k: K) -> int:
    return getattr(k, "n", z())

if __name__ == "__main__":
    assert f(K(7)) == 7
