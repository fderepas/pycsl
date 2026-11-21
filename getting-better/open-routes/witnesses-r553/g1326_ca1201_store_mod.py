from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import rt52dep4


#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    rt52dep4.gstore(xs)
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
