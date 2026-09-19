_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


def make() -> Inner:
    return Inner()


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    make().go(-1)
    return 0
