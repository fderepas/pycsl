r"""Test 6517 -- route #432 (expected PASS): CONTROL: `isinstance(x, str)` narrows a `Union[int, str]` is admitted. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Union

#@ no_exception \all
def f(x: Union[int, str]) -> int:
    if isinstance(x, str):
        return len(x.upper())
    return 0
