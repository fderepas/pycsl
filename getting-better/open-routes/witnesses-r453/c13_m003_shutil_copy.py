from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import shutil



#@ no_exception \all
def f(a: str, b: str) -> int:
    y = shutil.copy(a, b)
    return 1


if __name__ == "__main__":
    try:
        r = f('/nonexistent/x', '/tmp/y')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
