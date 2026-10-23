r"""G29 IE-C4b — a self dict field reset in the method, missing key read caught."""
from typing import Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    #@ assigns self.d
    #@ ensures \result == 0
    def run(self) -> int:
        self.d = {"a": 1}
        try:
            v = self.d["b"]
        except KeyError:
            return 9
        return v


if __name__ == "__main__":
    print("CPython:", C().run())
