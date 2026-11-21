from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    d: Dict[str, int]

    #@ no_exception \all
    def m(self) -> int:
        return 1 if self.d.get("k") < 5 else 0


if __name__ == "__main__":
    try:
        r = C({}).m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
