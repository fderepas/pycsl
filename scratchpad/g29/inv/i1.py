r"""G29 INV1 — an OUTSIDE store breaks a class invariant, then a method relying on it."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    c.x = -5
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe())
