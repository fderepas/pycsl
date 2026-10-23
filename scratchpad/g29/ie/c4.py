r"""self dict field missing key caught"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {"a": 1}

    #@ ensures \result == 0
    def run(self) -> int:
        try:
            v = self.d["b"]
        except KeyError:
            return 9
        return v


#@ ensures \result == 0
def probe() -> int:
    return C().run()


if __name__ == "__main__":
    print("CPython:", probe())
