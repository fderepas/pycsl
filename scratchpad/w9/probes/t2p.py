"""PROBE: `type(self)()` erased to literal 0 — observable through TRUTHINESS?"""
_ = 0  # anchor

class C:
    #@ requires True
    #@ ensures self.v == 7
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 7

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def make(self) -> int:
        o = type(self)()
        if o:
            return 7
        return 0

if __name__ == "__main__":
    print(C().make())
