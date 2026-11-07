r"""G29 INV8 — route #165 carrier: the receiver is a MODULE GLOBAL instance."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


G = C()


#@ ensures \result >= 0
def probe() -> int:
    G.x = -5
    return G.get()


if __name__ == "__main__":
    print("CPython:", probe())
