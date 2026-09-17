r"""G29 INV12 — #165 carrier: the receiver is a LIST ELEMENT whose invariant is broken."""
from typing import List
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
    cs: List[C] = [C()]
    cs[0].x = -5
    return cs[0].get()


if __name__ == "__main__":
    print("CPython:", probe())
