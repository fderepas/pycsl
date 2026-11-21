from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(tags: Set[str], groups: Dict[str, List[str]]) -> int:
    rest = tags.difference(groups.values())
    return len(rest)


if __name__ == "__main__":
    try:
        r = f({'a'}, {'g': ['a']})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
