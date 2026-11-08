r"""G29 INV4 — a method with a `requires` on its ARGUMENT, called with a violating argument on a local object."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1

    #@ requires k > 0
    #@ ensures \result > 0
    def get(self, k: int) -> int:
        return k


#@ ensures \result > 0
def probe() -> int:
    c = C()
    return c.get(-5)


if __name__ == "__main__":
    print("CPython:", probe())
