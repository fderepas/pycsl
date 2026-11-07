from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any

@dataclass
class D:
    x: int

DD = D

#@ no_exception \all
#@ ensures \result == 1
def g(d: DD) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
