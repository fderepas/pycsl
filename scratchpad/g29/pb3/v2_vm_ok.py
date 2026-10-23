_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    #@ verify_module GA
    #@ ensures \result == 7
    def seven(self) -> int:
        return 7

    #@ verify_module GB
    #@ ensures \result == 7
    def run(self) -> int:
        return self.seven()


def probe() -> int:
    c = C()
    return c.run()
