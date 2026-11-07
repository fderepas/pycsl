r"""guarded method through a dict-value receiver"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def get(self) -> int:
        return self.x // self.x


#@ ensures \result == 5
def probe() -> int:
    d: Dict[str, C] = {"a": C(0)}
    d["a"].get()
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
