class C:
    def __init__(self) -> None:
        self.rate = 0.5

#@ ensures \result == 0.5
def f() -> float:
    c = C()
    return c.rate
