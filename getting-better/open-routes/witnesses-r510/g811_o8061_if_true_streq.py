from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

S = "ab"


#@ ensures \result == True
def f() -> bool:
    return S == "ab"

if True:
    type S = int


if __name__ == "__main__":
    try:
        r = f()
        if r != True:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
