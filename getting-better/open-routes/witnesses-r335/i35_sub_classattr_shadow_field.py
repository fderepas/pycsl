#@ class invariant self.n >= 0
class B:
    def __init__(self) -> None:
        self.n = 0

class S(B):
    n = -1
    def __init__(self) -> None:
        pass

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.n

if __name__ == "__main__":
    assert f(S()) >= 0, f(S())
