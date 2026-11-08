r"""Test 3949 -- gen #37 route #309 (expected PASS): CONTROL: a constructor local's declared field with a call default proves `\result == 4`.
"""
# pycsl-expected: PASS
class K:
    def __init__(self, v: int) -> None:
        self.n = v

def z() -> int:
    return 0

#@ ensures \result == 4
def f() -> int:
    a = K(4)
    return getattr(a, "n", z())

if __name__ == "__main__":
    assert f() == 4
