r"""G29 INV9 — route #165 carrier: the receiver is a record FIELD of another object."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


class H:
    def __init__(self) -> None:
        self.c = C()


#@ ensures \result >= 0
def probe() -> int:
    h = H()
    h.c.x = -5
    return h.c.get()


if __name__ == "__main__":
    print("CPython:", probe())
