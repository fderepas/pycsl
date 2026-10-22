r"""Test 3696 -- gen #37 ch33 (expected FAIL): REFUSAL: a `for` over a call whose argument is an erased value (`g(func.get("body", []))`, the default lowers to `(any int)`) printed `variant { Array.length (g (... (any int))) - !i }` -- `any` is a PROGRAM expression and a variant is a LOGIC term (Why3 syntax error). Refused by name instead.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ ensures \length(\result) == \length(xs)
#@ assigns \nothing
def g(xs: List[int]) -> List[int]:
    return xs


#@ ensures \result >= 0
#@ assigns \nothing
def f(funcs: List[Any]) -> int:
    s = 0
    for func in funcs:
        for x in g(func.get("body", [])):
            s = s + 1
    return s
