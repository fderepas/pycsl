_ = 0  # anchor


class K:
    def __init__(self, k: int) -> None:
        self._key: int = k

    def __hash__(self) -> int:
        return self._key

    def __eq__(self, other: object) -> bool:
        return True


#@ ensures \result == 0
def probe() -> int:
    a = K(1)
    b = K(2)
    if a.__eq__(b):
        if a.__hash__() == b.__hash__():
            return 1
    return 99
