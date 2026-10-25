from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant \length(self.toks) >= 1
@mutable_state
class Cur:
    #@ requires len(toks) >= 1
    def __init__(self, toks: List[Tok]) -> None:
        toks = []
        self.toks: List[Tok] = toks

    #@ no_exception \all
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[0]


if __name__ == "__main__":
    try:
        Cur([Tok(7)]).cur()
        print("no violation")
    except IndexError as e:
        print("VIOLATION IndexError", e)
