from typing import Optional

class C:
    def __init__(self) -> None:
        self.k: int = 1
    def m(self) -> int:
        return 2


#@ no_exception \all
def f(c: Optional[C]) -> int:
    return c.m()


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
