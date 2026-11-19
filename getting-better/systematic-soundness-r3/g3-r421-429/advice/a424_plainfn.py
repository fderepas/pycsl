class K:
    def __init__(self) -> None:
        self.n: int = 1


def of(item: int) -> int:
    return item


#@ no_exception \all
def f() -> int:
    s = {of(1)}
    return len(s)
