_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    #@ assigns self.n
    #@ ensures self.n == 5
    #@ propagate_frame
    def setn(self) -> int:
        self.n = 5
        return 0

    #@ ensures \result == 0
    def run(self) -> int:
        self.setn()
        return self.n


def probe() -> int:
    c = C()
    return c.run()
