"""PROBE: an ANNOTATED self-field store in a NON-init method."""
_ = 0  # anchor

class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires self.v == 0
    #@ ensures \result == 0
    #@ assigns self.v
    def bump(self) -> int:
        self.v: int = 7
        return self.v

if __name__ == "__main__":
    print(C().bump())
