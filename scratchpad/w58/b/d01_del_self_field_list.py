from typing import List
class K:
    xs: List[int]
    def __init__(self) -> None:
        self.xs = [1, 2, 3]

    #@ ensures \result == 1
    def f(self) -> int:
        del self.xs[0]
        return self.xs[0]

if __name__ == "__main__":
    print(K().f())
