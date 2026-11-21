r"""Test 1693 - ROUTE #198 carrier (gen #30): a BARE `return` in an int-returning function was the integer ZERO. `stmt_control_flow._handle_return_stmt` lowered `val_ir is None` to the unit `"()"` and then to the literal `"0"`, so `raise (Return 0)` claimed the result IS zero. A bare `return` IS `return None` in Python, and the identical program spelled `return None` already REFUSED this contract (route #191's shared opaque `pycsl_none`) - one statement, two spellings, two answers, and one of them wrong. CPython answers `None` here, and `None == 0` is False; the TRUE twin (test 1694) was REFUSED, the decisive signature. The bare spelling now emits the SAME `pycsl_none`. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


#@ requires x > 0
#@ ensures \result == 0
def f(x: int) -> int:
    if x > 0:
        return
    return 5
