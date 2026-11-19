# FALSE: `s = {push(c) for y in [1]}` evaluates push(c), which sets c.v = 5; claim c.v unchanged (0).
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
    s = {push(c) for y in [1]}
    return c.v

if __name__ == "__main__":
    print(f(C()))
