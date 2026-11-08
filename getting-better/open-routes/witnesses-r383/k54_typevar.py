from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

from typing import TypeVar
T = TypeVar("T")

#@ no_exception \all
#@ ensures \result == 1
def g(d: T) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
