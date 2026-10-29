from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import shutil



#@ no_exception \all
#@ ensures \result == 7
def f(a: str) -> int:
    shutil.copy(a, a + 'x')
    return 7


if __name__ == "__main__":
    try:
        r = f('/nonexistent/rt36')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
