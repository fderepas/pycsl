#@ class invariant self.x >= 0
class C:
    #@ requires x >= 0
    def __init__(self, x: int) -> None:
        self.x = x

    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result >= 0
def f(c: C) -> int:
    return c.x

if __name__ == "__main__":
    print(f(C(-3)))
