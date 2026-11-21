r"""Test 8646 -- route #548 (control, expected PASS): `xs[0:1] = [5]` into a local int list, then `xs[0] + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    xs = [1, 2]
    xs[0:1] = [5]
    return xs[0] + 1


if __name__ == "__main__":
    print("result", f(1))
