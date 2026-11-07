from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class P:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ no_exception \all
    def m(self) -> int:
        type self = int
        return self.v


if __name__ == "__main__":
    try:
        r = P(1).m()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
