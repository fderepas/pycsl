#@ class invariant self.n == 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    n = 3
    def __init__(self, k: int) -> None:
        self.k = k

#@ ensures \result == 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S(1)) == 0, f(S(1))
