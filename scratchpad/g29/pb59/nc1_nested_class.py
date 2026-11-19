_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    class Inner:
        def __init__(self) -> None:
            self.n = 5

    i = Inner()
    return i.n
