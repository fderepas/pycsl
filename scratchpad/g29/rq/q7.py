r"""G29 RQ7 — a violated `requires` on a sibling self-call whose result is discarded."""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x

    #@ ensures \result == 5
    def run(self) -> int:
        self.x = 0
        self.get()
        return 5


#@ ensures \result == 5
def probe() -> int:
    return C(3).run()


if __name__ == "__main__":
    print("CPython:", probe())
