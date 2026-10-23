"""PROBE: a module-GLOBAL singleton field store `g.v = n` is a documented NO-OP."""
_ = 0  # anchor

class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

g = C()

#@ requires g.v == 0
#@ ensures \result == 0
def f() -> int:
    g.v = 7
    return g.v

if __name__ == "__main__":
    print(f())
