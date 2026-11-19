r"""nested class method call"""
from typing import List, Dict, Optional
_ = 0  # anchor


class Outer:
    class Inner:
        def __init__(self) -> None:
            self.v = 1

        def get(self) -> int:
            return self.v

    def __init__(self) -> None:
        self.k = 0


#@ ensures \result == 0
def probe() -> int:
    i = Outer.Inner()
    return i.get()


if __name__ == "__main__":
    print("CPython:", probe())
