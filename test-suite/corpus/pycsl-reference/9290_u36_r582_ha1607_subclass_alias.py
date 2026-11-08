r"""Test 9290 -- route #582 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R582-CLASS-BODY-ALIAS-CALL in every model; red team 55 probe ha1607_subclass_alias.py): a SUBCLASS body alias `class S(C): n = C.m`, `c: S`, `c.n(5)`; CPython caller(S()) == 5 under `ensures \result == 0`
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


#@ assigns c.a
def g(c: C, v: int) -> None:
    c.a = v



@mutable_state
class S(C):
    n = C.m


#@ requires c.a == 0
#@ ensures \result == 0
#@ assigns c.a
def caller(c: S) -> int:
    c.n(5)
    return c.a


if __name__ == "__main__":
    try:
        r = caller(S())
        if r != 0:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
