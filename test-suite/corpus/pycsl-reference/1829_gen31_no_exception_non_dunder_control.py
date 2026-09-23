r"""Test 1829 — gen #31 CONTROL for 1828 (expected FAIL): the same body under a plain name.

One identifier apart from 1828. It FAILED before route #219's repair and FAILS after, which
is what makes 1828 a ROUTE rather than a missing feature: the `#@ no_exception` checker was
never broken, it was switched off by the method's NAME.

The scope was measured rather than guessed. The identical body and contract were run as a
plain method, a `@staticmethod`, a `@classmethod`, a `@property`, a nested function and a
module-level function. Every one FAILS or is REFUSED. ONLY the dunder spelling evaded — so
the repair is exactly "stop dropping dunders" and nothing wider.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ no_exception \all
    def enter(self) -> int:
        d: int = 0
        return 10 // d
