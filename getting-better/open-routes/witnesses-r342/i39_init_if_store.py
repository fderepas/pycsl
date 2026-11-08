#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        if self.x == 0:
            self.x = 5

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
