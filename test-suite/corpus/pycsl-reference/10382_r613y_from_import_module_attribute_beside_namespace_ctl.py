r"""Test 10382 -- run #9 u66, review rt76 r5 control (PASS; u64's V2D refused it). The --import-path root
multi_file_lib/u66/X5 holds a MODULE zq80.py defining b() and a namespace directory zq80/ holding b.py.
CPython takes the module (FileFinder prefers it to a bare directory), and `from zq80 import b` binds the
module's function, never a submodule: `cd <tree root> && PYTHONPATH=<X5> python <this file>` prints
"result 1".
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/u66/X5
from zq80 import b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return b()


if __name__ == "__main__":
    print("result", g())
