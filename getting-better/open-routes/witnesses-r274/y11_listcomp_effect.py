# FALSE: list comprehension body call push(c) mutates c.v.
class C:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures \result == 1
#@ assigns c.v
def push(c: C) -> int:
    c.v = 5
    return 1

#@ requires c.v == 0
#@ ensures \result == 0
#@ assigns c.v
def f(c: C) -> int:
    xs: list[int] = [1]
    ys = [push(c) for y in xs]
    return c.v

if __name__ == "__main__":
    print(f(C()))
