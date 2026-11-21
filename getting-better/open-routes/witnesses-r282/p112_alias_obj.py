class A:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures b.v == \old(b.v)
#@ assigns a.v
def f(a: A, b: A) -> None:
    a.v = b.v + 1

if __name__ == "__main__":
    x = A(); f(x, x); print(x.v); assert x.v == 0
