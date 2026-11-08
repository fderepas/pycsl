r"""Test 8125 -- route #517 (expected FAIL: PROVED at base, REFUSED PYCSL-R517-TYPE-PARAM-NAME-READ; red team 47 probe a9010_class_tp_method_div): `class C[K]:` around a method reading K; CPython C().m(10) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


class C[K]:
    #@ no_exception \all
    def m(self, n: int) -> int:
        return n // K


if __name__ == "__main__":
    try:
        r = C().m(10)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
