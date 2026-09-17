r"""G29 INV10 — #165 carrier: the method is INHERITED; the receiver is a SUBCLASS local."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


class D(C):
    pass


#@ ensures \result >= 0
def probe() -> int:
    d = D()
    d.x = -5
    return d.get()


if __name__ == "__main__":
    print("CPython:", probe())
