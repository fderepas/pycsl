r"""G29 INV11 — #165 carrier: the receiver's invariant is broken, and the method's ensures is PARAM-referencing."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= k
    def get(self, k: int) -> int:
        return self.x + k


#@ ensures \result >= 3
def probe() -> int:
    c = C()
    c.x = -5
    return c.get(3)


if __name__ == "__main__":
    print("CPython:", probe())
