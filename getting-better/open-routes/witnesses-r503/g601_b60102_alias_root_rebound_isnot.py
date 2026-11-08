from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == False
def f(n: int) -> bool:
    a = n * 1000
    b = a
    a = n * 1000
    return a is not b


if __name__ == "__main__":
    try:
        r = f(7)
        if r != False:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
