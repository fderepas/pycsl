r"""G29 IE-J13 — missing key read in a method, caught in the caller method."""
from typing import Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    def get(self) -> int:
        return self.d["zz"]

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            v = self.get()
        except KeyError:
            return 9
        return v


if __name__ == "__main__":
    print("CPython:", C().run())
