class C:
    def __init__(self) -> None:
        self.v: int = 0
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self, x: int) -> int:
        if x < 0:
            raise ValueError("neg")
        return 0

if __name__ == "__main__":
    assert C().m(-1) == 0
