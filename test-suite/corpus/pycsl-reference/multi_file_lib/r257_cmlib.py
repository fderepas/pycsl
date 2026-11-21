"""r257_cmlib — the context-manager CLASS imported by the route #257 witnesses 2560, 2565-2568.

`Counter.__enter__` WRITES `self.n`. A bare `with` over a Counter, in a file that imports it,
used to be lowered to its body alone, so the write was lost in the model.
"""


class Counter:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def __enter__(self) -> int:
        self.n = self.n + 1
        return 0

    #@ ensures \result == False
    #@ assigns \nothing
    def __exit__(self, a: object, b: object, c: object) -> bool:
        return False
