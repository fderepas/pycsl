# ROUTE #219 CONTROL (expects FAILED today — the honest verdict).
#
# Byte-for-byte route219-carrier-no-exception-inside-a-dunder.py with `__enter__` renamed
# to `enter`. ONE IDENTIFIER APART. This is what makes #219 a route rather than a missing
# feature: the checker exists, works, and is switched off by the method's NAME.
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ no_exception \all
    def enter(self) -> int:
        d: int = 0
        return 10 // d
