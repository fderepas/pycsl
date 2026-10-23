r"""Test 1641 - ROUTE #181 (gen #29): the imported raising constructor `C(-1)` under `#@ no_exception ValueError` PROVED (CPython ValueError).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r181_raising import C


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    c = C(-1)
    return 0
