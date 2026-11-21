class C:
    rate: float
    def __init__(self) -> None:
        self.rate: float = 0.5

#@ ensures \result == 0.5
def f() -> float:
    c = C()
    return c.rate
