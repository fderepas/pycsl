class C:
    sep: str
    def __init__(self) -> None:
        self.sep: str = "ab"

#@ ensures \result == 0
def f() -> int:
    c = C()
    return len(c.sep)
