r"""Test 1778 — WITNESS: `Literal[SomeName]`, a literal that is not int/str/bool/None.

L4 / L5c / PEP 586. Only int, str, bool and None literals are supported; an Enum member or
a bare name denotes a value the lowering has no representation for, so it is refused
rather than guessed at. One of the refusals `bin/check-refusal-witness-coverage.py`
measured as having no witness.
"""
# pycsl-expected: FAIL
from typing import Literal

_ = 0  # anchor


#@ ensures \result >= 0
def pick(x: Literal[SomeName]) -> int:
    return 0
