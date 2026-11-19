r"""G29 INV2 — an invariant broken INSIDE a method mid-body, then a call to another method of self."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x

    #@ ensures \result >= 0
    def m(self) -> int:
        self.x = -5
        r = self.get()
        self.x = 1
        return r


if __name__ == "__main__":
    print("CPython:", C().m())
