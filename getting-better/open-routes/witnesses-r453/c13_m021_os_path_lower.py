from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import os



#@ no_exception \all
def f(s: str) -> int:
    y = os.path.lower(s)
    return 1


if __name__ == "__main__":
    try:
        r = f('a')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
