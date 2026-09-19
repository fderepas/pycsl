_ = 0  # anchor

from lib3 import Inner


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        self.inner.go(-1)
        return 0
