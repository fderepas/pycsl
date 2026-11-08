from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


def mk_assert() -> int:
    assert False
    return 0


@dataclasses.dataclass
class P:
    a: int = dataclasses.field(default_factory=mk_assert)


#@ no_exception \all
def f() -> int:
    p = P()
    return 1


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
