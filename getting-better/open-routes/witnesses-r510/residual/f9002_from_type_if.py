from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from dep900_type_if import g


#@ ensures \result == 3
def f() -> int:
    return g(3)


if __name__ == "__main__":
    try:
        r = f()
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
