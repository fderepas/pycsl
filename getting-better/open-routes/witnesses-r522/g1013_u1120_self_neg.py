from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ no_exception \all
    def m(self) -> int:
        return -self.d.get("k")


if __name__ == "__main__":
    try:
        r = C().m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
