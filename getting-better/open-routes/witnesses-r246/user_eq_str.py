from typing import Any


#@ requires x == y
#@ ensures isinstance(x, str) == isinstance(y, str)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


class W:
    def __eq__(self, o: object) -> bool:
        return True


if __name__ == "__main__":
    print(W() == "s", isinstance(W(), str) == isinstance("s", str))
