from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import os



#@ no_exception \all
def f(a: str) -> int:
    y = os.replace(a, a)
    return 1


if __name__ == "__main__":
    try:
        r = f('/nonexistent/rt36')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
