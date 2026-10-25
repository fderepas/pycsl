r"""Test 4955 -- gen #37 route #226 (expected FAIL): a PARAMLESS `__init__` storing the literal `self.n = 0` and `self.name = "a"` under `#@ class invariant self.n >= 5`. Increment 1 required EVERY field to be an int, so the `str` field meant no goal and `ensures \result >= 5` on `c.n` PROVED (CPython 0). The projection states `forall n. n = 0 -> n >= 5`, which FAILS.
"""
# pycsl-expected: FAIL
#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = 0
        self.name = "a"

#@ ensures \result >= 5
def read(c: C) -> int:
    return c.n

if __name__ == "__main__":
    assert read(C()) == 0
