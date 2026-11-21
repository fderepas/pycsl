from typing import List
class C:
    n: int
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)

#@ ensures \result == 3
def f() -> int:
    c = C([1, 2, 3])
    return c.n
if __name__ == "__main__":
    print(f())
