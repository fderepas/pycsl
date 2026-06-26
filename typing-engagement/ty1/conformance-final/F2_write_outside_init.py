"""Static gate F2- — writing a Final instance attribute outside __init__ is an error.

Spec clause F2 (final-twoplane-spec.md §1.2, S5 case (b)): an instance
attribute annotated `attr: Final[T]` in class `C` may be written ONLY
inside `C.__init__`. A write to `self.attr` in a method `m` other than
`__init__` is a static error, raised by the syntactic write-site check
(F2 arm of `_check_final`, a degenerate HAPPY no-write confinement — NOT
a VC).

The runtime would execute the write (FR3 — no enforcement); the
rejection is a static-plane judgment only (FD1 divergence, FD2 no-blend).

Expected (from spec): FAIL (PIPELINE ERROR) — the syntactic write-site
check raises `PyCSLSemanticError` at the semantic-analysis stage, before
any WhyML is emitted.
"""

from typing import Final


class C:
    attr: Final[int]

    def __init__(self):
        self.attr = 0

    def m(self) -> int:
        self.attr = 1
        return self.attr


if __name__ == "__main__":
    obj = C()
    assert obj.m() == 1
    print("PASS")
