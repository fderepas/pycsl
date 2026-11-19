_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 0

    def __bool__(self) -> bool:
        return False


#@ ensures \result == 99
def probe() -> int:
    a = C()
    if a:
        return 1
    return 0
