from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.z: int = 0

    def g(self, k: int) -> Tuple[int, Any]:
        return (1, None)

    #@ no_exception \all
    def f(self, k: int) -> int:
        t = self.g(k)
        return 1 if t[1] < k else 0


if __name__ == "__main__":
    try:
        print("result", repr(C().f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
