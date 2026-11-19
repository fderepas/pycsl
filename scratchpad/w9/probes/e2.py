"""PROBE: an erased set-literal SELF FIELD used as a guard."""
_ = 0  # anchor
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.s
    def __init__(self) -> None:
        self.s: set = {1, 2, 3}

    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def g(self) -> int:
        if self.s:
            return 7
        return 0
if __name__ == "__main__":
    print(C().g())
