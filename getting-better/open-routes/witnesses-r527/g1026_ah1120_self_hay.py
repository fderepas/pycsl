from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    def __init__(self) -> None:
        self.s: Optional[str] = None

    #@ no_exception \all
    def m(self) -> int:
        return 1 if "a" in self.s else 0


if __name__ == "__main__":
    try:
        r = K().m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
