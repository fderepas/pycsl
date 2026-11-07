from dataclasses import dataclass, field
from typing import List


#@ class invariant \length(self.xs) == 5
@dataclass
class D:
    xs: List[int] = field(default_factory=lambda: [0] * 4)

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.xs[4]


if __name__ == "__main__":
    try:
        D().last()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
