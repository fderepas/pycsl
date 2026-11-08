_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    def __eq__(self, other: object) -> bool:
        return False


#@ ensures \result == -1
def probe() -> int:
    a = C()
    b = C()
    if a == b:
        return 1
    return 0
