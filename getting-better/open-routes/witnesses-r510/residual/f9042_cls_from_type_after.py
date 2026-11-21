from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from dep900c_type_after import C


#@ ensures \result == 3
def f() -> int:
    c = C(3)
    return c.get()


if __name__ == "__main__":
    try:
        r = f()
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
