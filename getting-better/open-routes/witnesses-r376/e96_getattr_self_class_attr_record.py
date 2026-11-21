class R:
    k = -1
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def m(self) -> int:
        return getattr(self, "k", 0)

if __name__ == "__main__":
    assert R().m() >= 0, R().m()
