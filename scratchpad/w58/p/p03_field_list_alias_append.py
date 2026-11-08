from typing import List
class K:
    xs: List[int]
    def __init__(self) -> None:
        self.xs = [1, 2]

    #@ ensures \result == 2
    def f(self) -> int:
        b: List[int] = self.xs
        b.append(3)
        return len(self.xs)
if __name__ == "__main__":
    print(K().f())
