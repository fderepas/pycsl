r"""Test 1617 - ROUTE #176 carrier (gen #29): an IMPORTED class's `go` raises ValueError on a negative argument; `c.go(-1)` inside `try ... except ValueError: return 9` PROVED `\result == 0` at HEAD (CPython 9). The imported method's escaping exception now reaches the handler.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r176_raising import C


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go(-1)
    except ValueError:
        return 9
    return 0
