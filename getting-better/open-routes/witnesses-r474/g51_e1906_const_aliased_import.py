from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h1906 import K as Z


#@ no_exception \all
def f(n: int) -> int:
    return n // Z


if __name__ == "__main__":
    try:
        print('result', f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
