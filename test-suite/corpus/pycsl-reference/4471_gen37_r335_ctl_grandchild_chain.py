r"""Test 4471 -- gen #37 route #335 (control, expected PASS): control: `S(B)` with `super().__init__(); self.m = 1`, grandchild `G(S): pass`, great-grandchild `H(G)` with `super().__init__()`. PROVED. 
"""
# pycsl-expected: PASS
#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        self.m = 1

class G(S):
    pass

class H(G):
    def __init__(self) -> None:
        super().__init__()

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(G()) >= 0 and f(H()) >= 0
