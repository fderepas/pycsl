from typing import List
class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

#@ ensures \result == 1
def f() -> int:
    a = C(1)
    xs: List[C] = [a]
    a.v = 2
    return xs[0].v
if __name__ == "__main__":
    print(f())
