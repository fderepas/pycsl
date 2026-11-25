r"""Test 10492 -- run #9 u75, route #635 (FAIL). A DEPENDENCY function (zu75c_run.run) imports `timeit` and
runs a source string that replaces the submodule attribute `zu75c.b` with zu75c.c; the program calls it,
so `cd <tree root> && python <this file>` prints "result 2". Route #326 judges only the program's imports
(main L21 refuses this file through route #483, which follows the top-level call into the function).
REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (u75: any reached module other than the program importing a
standard-library module that imports by name or runs source strings).
"""
# pycsl-expected: FAIL
import zu75c.b
from zu75c_run import run

run()


#@ ensures \result == 1
def g() -> int:
    return zu75c.b.one()


if __name__ == "__main__":
    print("result", g())
