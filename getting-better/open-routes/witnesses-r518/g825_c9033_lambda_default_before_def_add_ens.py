from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5
_l = lambda a=(K := 0): a


#@ ensures \result == 6
def f() -> int:
    return K + 1


if __name__ == "__main__":
    try:
        r = f()
        if r != 6:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
