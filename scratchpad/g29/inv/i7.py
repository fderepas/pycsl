r"""G29 INV7 — route #165 carrier: the receiver is a PARAMETER whose invariant the caller breaks."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


#@ ensures \result >= 0
def probe(c: C) -> int:
    c.x = -5
    return c.get()


if __name__ == "__main__":
    print("CPython:", probe(C()))
