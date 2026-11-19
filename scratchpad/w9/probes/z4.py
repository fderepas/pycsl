_ = 0  # anchor
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a: int = 0
        self.b: int = 0
    #@ requires self.a == 0
    #@ ensures \result == 0
    #@ assigns self.a, self.b
    def s(self) -> int:
        self.a = self.b = 7
        return self.a
if __name__ == "__main__":
    print(C().s())
