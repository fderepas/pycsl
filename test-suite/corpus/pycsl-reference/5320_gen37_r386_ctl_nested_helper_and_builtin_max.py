r"""Test 5320 -- gen #37 route #386 (expected PASS): control: a nested def not named like a builtin, and the builtin `max` in the same method; PROVED.
"""
# pycsl-expected: PASS
class W:
    def __init__(self) -> None:
        self.a: int = 3

    #@ ensures \result >= self.a
    #@ assigns \nothing
    def m(self) -> int:
        def helper(x: int) -> int:
            return x
        return max(self.a, 1)


if __name__ == "__main__":
    r = W().m()
    assert r == 3
