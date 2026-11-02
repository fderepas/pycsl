from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dep900_type_after


#@ no_exception \all
def f() -> int:
    return dep900_type_after.g(3)


if __name__ == "__main__":
    try:
        r = f()
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
