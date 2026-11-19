r"""Test 9176 -- route #573 (expected FAIL: PROVED at base `no_exception \all`, REFUSED the route #252 erased-value refusal (`an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as a builtin type`); a new false proof beyond red team 54's family, measured PROVED at base 8358d5d31): `t = g(k); return t[1] + 1`; CPython TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
"""
# pycsl-expected: FAIL
from typing import Any, List, Tuple, Optional, Dict
def g(k: int) -> Tuple[object, ...]:
    return (1, None)
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return t[1] + 1

if __name__ == "__main__":
    print(f(1))
