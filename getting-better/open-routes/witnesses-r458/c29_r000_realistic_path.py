from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(base: str, name: str) -> int:
    full = base / name
    return len(full)


if __name__ == "__main__":
    try:
        r = f('/etc', 'hosts')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
