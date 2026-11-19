r"""Test 9173 -- route #573 (expected FAIL: PROVED at base `no_exception \all`, REFUSED the route #252 erased-value refusal (`an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as a builtin type`); red team 54 probe fe1520_variadic_any.py): `t = g(k); return t[1] + 1`; CPython TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, ...]:
    return (1, None)
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return t[1] + 1


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
