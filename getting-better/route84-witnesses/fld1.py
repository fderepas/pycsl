class C:
    v: int
    #@ assigns self.v
    def __init__(self) -> None:
        self.v = 1

#@ requires True
#@ ensures \result == 0
#@ assigns c.v
def bump(c: C) -> int:
    c.v = 7
    return 0

#@ ensures \result == 1
def f() -> int:
    c = C()
    assert bump(c) == 0
    return c.v
if __name__ == "__main__":
    print(f())
