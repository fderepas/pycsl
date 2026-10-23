"""PROBE: computed-rhs-erasure site 1 — `x = type(self)(...)` erased to 0?"""
_ = 0  # anchor

class C:
    #@ requires True
    #@ ensures self.v == 7
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 7

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def make(self) -> int:
        o = type(self)()
        return o.v

if __name__ == "__main__":
    print(C().make())
