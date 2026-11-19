from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(n: int) -> int:
    return n


#@ no_exception \all
def f[g](n: int) -> int:
    return g(n) + 1


if __name__ == "__main__":
    try:
        r = f(1)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
