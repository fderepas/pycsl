"""Test 0737 — negative: writing a `Final` instance attribute outside __init__ (F2).

typing-engagement ty1 (27-0000-typing-spec-3): an instance attribute annotated
`attr: Final[T]` in class `C` may be written ONLY inside `C.__init__`. A write
to `self.attr` in a method `m` other than `__init__` is a static error, raised
by `core_ir_semantic._check_final` (F2 arm — a syntactic write-site check, NOT
a VC). The run terminates with a PIPELINE ERROR (exit 1). The runtime would
execute the write (FR3 — no enforcement); the rejection is a static-plane
judgment only (FD1 divergence).
"""
# pycsl-expected: FAIL
from typing import Final


class C:
    attr: Final[int]

    def __init__(self):
        self.attr = 0

    def m(self) -> int:
        self.attr = 1
        return self.attr
