r"""Test 4474 -- gen #37 route #335 (control, expected PASS): control: a fieldless mixin WITHOUT `__init__` first in `class S(M, B)`: the MRO walks through it to `B.__init__`. PROVED. 
"""
# pycsl-expected: PASS
class M:
    def helper(self) -> int:
        return 1

#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(M, B):
    pass

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0
