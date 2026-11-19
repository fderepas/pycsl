r"""Test 8647 -- route #548 (control, expected PASS): `xs[0:1] = [None]`, then the read is narrowed: `if xs[0] is not None: return xs[0] + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    xs = [1, 2]
    xs[0:1] = [None]
    if xs[0] is not None:
        return xs[0] + 1
    return 0


if __name__ == "__main__":
    print("result", f(1))
