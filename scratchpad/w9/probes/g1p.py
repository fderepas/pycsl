"""PROBE: does `getattr(obj, "field", default)` erase a REAL attribute read to 0?"""
_ = 0  # anchor

class C:
    #@ requires True
    #@ ensures self.a == 7
    #@ assigns self.a
    def __init__(self) -> None:
        self.a: int = 7

    #@ requires self.a == 7
    #@ ensures \result == 7
    #@ assigns \nothing
    def get(self) -> int:
        v = getattr(self, "a", 0)
        if v:
            return 7
        return 0

if __name__ == "__main__":
    print(C().get())
