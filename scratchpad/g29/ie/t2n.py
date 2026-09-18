r"""attribute on None with no try: ambient"""
from typing import Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.x = 1


#@ ensures \result == 5
def probe() -> int:
    c: Optional[C] = None
    v = c.x
    return v * 0 + 5


if __name__ == "__main__":
    print("CPython:", probe())
