r"""Test 6519 -- route #432 (expected FAIL): `assert x is not None` NARROWS (the access `x.strip()` after it is NOT refused by #432), and the proof then FAILS on the assert's own AssertionError obligation under `no_exception \all` (`x` may be None) -- the sound outcome, FAIL at base 1c083dcbe and candidate alike.
"""
# pycsl-expected: FAIL
from typing import Optional

#@ no_exception \all
def f(x: Optional[str]) -> int:
    assert x is not None
    return len(x.strip())
