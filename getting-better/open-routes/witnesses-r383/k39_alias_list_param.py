from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

DL = List[D]

#@ no_exception \all
#@ requires \length(ds) >= 1
#@ ensures \result == 1
def g(ds: DL) -> int:
    s = {ds[0]}
    return 1

if __name__ == "__main__":
    print(g([D(1)]))
