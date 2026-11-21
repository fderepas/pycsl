r"""Test 4473 -- gen #37 route #335 (control, expected PASS): control: `super().__init__()` then `self.n = 5`. PROVED. 
"""
# pycsl-expected: PASS
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        self.n = 5

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0
