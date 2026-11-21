from dataclasses import dataclass, field
from typing import List


@dataclass
class T:
    xs: List[int] = field(default_factory=list)
    ys: List[int] = field(default_factory=list)

    #@ requires \length(self.xs) == 1 and \length(self.ys) == 1
    #@ requires self.ys[0] == 0
    #@ ensures \result == 0
    #@ assigns self.xs
    def poke(self) -> int:
        self.xs[0] = 7
        return self.ys[0]


if __name__ == "__main__":
    L = [0]
    print(T(L, L).poke())
