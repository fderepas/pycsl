from typing import List


class C:
    def __init__(self, n: int) -> None:
        self.n = n

    def size(self) -> int:
        return 1


#@ no_exception \all
def f(xs: List[C]) -> int:
    return xs[3].size()

if __name__ == "__main__":
    print(f([]))
