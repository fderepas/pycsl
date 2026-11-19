r"""Test 1639 - ROUTE #181 (gen #29): an IMPORTED class whose `__init__` raises ValueError, constructed as `C(-1)` inside `try ... except ValueError: return 9`, PROVED `\result == 0` (CPython 9): route #179's source check read the main file only. Dependency modules are now parsed too.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r181_raising import C


#@ ensures \result == 0
def probe() -> int:
    try:
        c = C(-1)
    except ValueError:
        return 9
    return 0
