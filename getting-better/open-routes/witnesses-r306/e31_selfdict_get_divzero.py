from typing import Dict

class C:
    def __init__(self) -> None:
        self.d: Dict[int, int] = {1: 1}

    #@ no_exception \all
    #@ ensures \result == 1
    def m(self, x: int) -> int:
        return self.d.get(1, 10 // x)

if __name__ == "__main__":
    assert C().m(0) == 1
