r"""Test 6692 -- routes #440 / #441 (expected PASS): CONTROL: container and int methods with rows in the signature table on DERIVED receivers (`list.append` / `count`, `dict.get` with a default, `int.bit_length`), each under `#@ no_exception \all`. Admitted; PROVED at candidate (CPython ok).
"""
# pycsl-expected: PASS
from typing import Dict, List


#@ no_exception \all
def f1(xs: List[int]) -> int:
    ys = [1, 2]
    ys.append(3)
    return len(ys) + xs.count(1)


#@ no_exception \all
def f2(d: Dict[str, int]) -> int:
    return d.get("a", 0)


#@ no_exception \all
def f3(n: int) -> int:
    return n.bit_length()


if __name__ == "__main__":
    print(f1([1]), f2({"a": 2}), f3(5))
