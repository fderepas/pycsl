r"""Test 9289 -- route #582 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R582-CLASS-BODY-ALIAS-CALL in every model; red team 55 probe ha1603_cls_alias_unbound_call.py): the unbound call `C.n(c, 5)`; CPython caller(C()) == 5 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures self.a == v
    #@ assigns self.a
    def m(self, v: int) -> None:
        self.a = v

    n = m


#@ assigns c.a
def g(c: C, v: int) -> None:
    c.a = v



#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: C) -> int:
    C.n(c, 5)
    return c.a


if __name__ == "__main__":
    try:
        r = caller(C())
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
