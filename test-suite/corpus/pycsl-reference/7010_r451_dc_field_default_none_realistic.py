r"""Test 7010 -- route #451 (expected FAIL): red-team 36 probe c11_q009_realistic_config -- `@dataclass` field `name: str = None`, then `c.name.strip()` (CPython AttributeError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
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
