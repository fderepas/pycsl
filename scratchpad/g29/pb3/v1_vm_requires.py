_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    #@ verify_module GA
    #@ requires v != 0
    #@ ensures \result == 10 // v
    def div(self, v: int) -> int:
        return 10 // v

    #@ verify_module GB
    #@ ensures \result == 0
    def run(self) -> int:
        self.div(0)
        return 0


def probe() -> int:
    c = C()
    return c.run()
