# ROUTE #219 CARRIER (expects SUCCESS today — the false certificate).
#
# `#@ no_exception \all` over a body whose only statement divides by zero. Rename
# `__enter__` to `enter` and the identical file FAILS. CPython raises ZeroDivisionError.
# PyCSL says "All contracts formally proven" because `_should_skip_method` drops every
# dunder before any IR is built, so the method is not in `ir_data["functions"]` and no
# check, no VC and no UB detector ever sees it.
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ no_exception \all
    def __enter__(self) -> int:
        d: int = 0
        return 10 // d
