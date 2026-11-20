r"""Test 10306 -- run #8 u58, review rt69 G5 (PASS control). `multi_file_lib/` beside the program is a bare
namespace directory (no `__init__.py`) whose name no other root CPython searches holds (no --import-path,
stdlib or site-directory entry), so the namespace has exactly this one portion and CPython loads the file
pycsl reads. Emitted.
"""
# pycsl-expected: PASS
from multi_file_lib.r613y.nsctl import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()


if __name__ == "__main__":
    print("result", f())
