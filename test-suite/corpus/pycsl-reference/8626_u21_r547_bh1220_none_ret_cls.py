r"""Test 8626 -- route #547 (expected FAIL: PROVED at base int28, now REFUSED PYCSL-R490-LITERAL-INT-HASH; red team 52 probe g1307_bh1220_none_ret_cls): `Q.m(k) + 1` of a `@staticmethod def m(k: int) -> int: return None`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    @staticmethod
    def m(k: int) -> int:
        return None


#@ no_exception \all
def f(k: int) -> int:
    return Q.m(k) + 1


if __name__ == "__main__":
    try:
        r = f(0)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
