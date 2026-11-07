r"""Test 1746 — WITNESS for `PYCSL-SEM-NORETURN`: a `-> NoReturn` whose body can return.

`NoReturn` is a `false` postcondition in the model, so declaring it on a body with no
`raise` and no non-terminating construct would make everything after the call provable.
The refusal requires the declaration to be JUSTIFIED by the body. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it fires.
"""
# pycsl-expected: FAIL
from typing import NoReturn

_ = 0  # anchor


#@ requires n >= 0
def f(n: int) -> NoReturn:
    pass
