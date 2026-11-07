r"""Test 1588 - ROUTE #171 (gen #29): `xs: List[int] = []; try: v = xs[0] except IndexError: return 9; return v * 0` PROVED `\result == 0` (CPython 9): the empty literal is a 1024-cell placeholder, so the read cannot fail in the model and the handler was dead. A function whose try catches a modelled implicit exception is now checked as if it declared `no_exception` for it.
"""
# pycsl-expected: FAIL
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    try:
        v = xs[0]
    except IndexError:
        return 9
    return v * 0
