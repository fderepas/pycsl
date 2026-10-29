from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

from h1705 import S


#@ no_exception \all
def f(n: int) -> str:
    return S[1]


if __name__ == "__main__":
    try:
        print('result', f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
