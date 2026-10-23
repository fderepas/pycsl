r"""G29 INV3 — a method with a `requires` on self, called on a local object that violates it."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1

    #@ requires self.x > 0
    #@ ensures \result > 0
    def get(self) -> int:
        return self.x


#@ ensures \result > 0
def probe() -> int:
    c = C()
    c.x = -5
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe())
