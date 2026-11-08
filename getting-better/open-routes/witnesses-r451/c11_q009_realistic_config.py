from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

@dataclass
class Config:
    path: str
    name: str = None  # type: ignore
    retries: int = 3



#@ no_exception \all
def f(path: str) -> int:
    c = Config(path)
    return len(c.name.strip())


if __name__ == "__main__":
    try:
        r = f('/etc/x')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
