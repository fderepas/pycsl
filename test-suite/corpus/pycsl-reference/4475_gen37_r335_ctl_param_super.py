r"""Test 4475 -- gen #37 route #335 (control, expected PASS): control: `super().__init__(3)` into a parameterised base constructor (`#@ requires k >= 0`). PROVED. 
"""
# pycsl-expected: PASS
#@ class invariant self.n >= 0
class B:
    #@ requires k >= 0
    def __init__(self, k: int) -> None:
        self.n = k

class S(B):
    def __init__(self) -> None:
        super().__init__(3)

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0
