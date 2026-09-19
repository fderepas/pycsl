_ = 0  # anchor


class Widget:
    def __init__(self) -> None:
        self.n = 7

    #@ ensures \result == 7
    def get(self) -> int:
        return 7
