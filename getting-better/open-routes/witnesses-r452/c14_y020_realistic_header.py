from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(sep: int) -> int:
    data = b'GET / HTTP/1.1'
    return data.find(sep)


if __name__ == "__main__":
    try:
        r = f(0x100)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
