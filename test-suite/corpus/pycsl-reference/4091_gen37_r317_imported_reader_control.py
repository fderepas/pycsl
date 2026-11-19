r"""Test 4091 -- gen #37 route #317 (expected PASS): CONTROL: an imported function that only reads its list argument gets no `writes`; the caller proves `ys[0] == 0`.
"""
# pycsl-expected: PASS
from typing import List
from multi_file_lib.rt16ctl import peek

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    peek(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
