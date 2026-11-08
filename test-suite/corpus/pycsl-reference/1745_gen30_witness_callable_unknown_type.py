r"""Test 1745 — WITNESS for `PYCSL-TY3-CALLABLE-SCOPE`: a `Callable` whose argument or
return type is not a type the model knows.

`Callable[[int], "Nope"]` names a return type that is neither a builtin scalar nor a
declared class, so the annotation cannot be lowered and is refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
from typing import Callable

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int, g: Callable[[int], "Nope"]) -> int:
    return 0
