#@ class invariant self.x >= 0
class C:
    def __init__(self, x: int = 0) -> None:
        self.x = 5
        self.x = x - 10

#@ ensures \result >= 0
def f(c: C) -> int:
    return c.x

if __name__ == "__main__":
    print(f(C()))
