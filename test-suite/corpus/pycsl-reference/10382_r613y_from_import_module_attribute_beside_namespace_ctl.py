r"""Test 10382 -- run #9 u66, review rt76 r5 control (PASS; u64's V2D refused it). The program's directory
(the corpus directory, sys.path[0]) holds a MODULE zq80.py defining b() and a namespace directory zq80/ holding
b.py. CPython takes the module (FileFinder prefers it to a bare directory), and `from zq80 import b` binds the
module's function, never a submodule: `cd <tree root> && python <this file>` prints "result 1".
"""
# pycsl-expected: PASS
from zq80 import b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return b()


if __name__ == "__main__":
    print("result", g())
