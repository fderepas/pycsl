_ = 0  # anchor

from lib2 import Widget as W


class Widget:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


#@ ensures \result == 1
def probe() -> int:
    w = W()
    return w.get()
