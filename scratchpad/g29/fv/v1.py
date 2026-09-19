r"""callee reached through a field receiver, missing key"""
from typing import List, Dict
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["zz"]


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            v = self.inner.get()
        except KeyError:
            return 9
        return v * 0


if __name__ == "__main__":
    print("CPython:", Outer().run())
