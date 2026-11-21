from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = a
    a = n + 1000
    return a is b


if __name__ == "__main__":
    try:
        r = f(5)
        if r != True:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
