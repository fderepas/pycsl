from typing import Dict
class R:
    def __init__(self) -> None:
        self.x = 0
    __hash__ = None  # type: ignore

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    d: Dict[int, int] = {}
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
