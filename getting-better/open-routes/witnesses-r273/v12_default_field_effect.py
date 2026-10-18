# FALSE: nested def default push(c) sets c.v = 5 (field version of v09).
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
    def inner(y: int = push(c)) -> int:
        return y
    return c.v

if __name__ == "__main__":
    print(f(C()))
