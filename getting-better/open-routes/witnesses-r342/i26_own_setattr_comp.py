#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        if (y := 5) > 0:
            self.x = self.x
        [setattr(self, "x", 5) for _ in range(1)]

#@ no_exception \all
#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
