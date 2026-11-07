from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ no_exception \all
def f(n: int) -> int:
    class K:
        v = 1
    return n + K


if __name__ == "__main__":
    try:
        r = f(1)
        if r != 6:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
