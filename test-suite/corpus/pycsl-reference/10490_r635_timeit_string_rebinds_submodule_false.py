r"""Test 10490 -- run #9 u75, review rt83 s2, route #635 (FAIL, PRE-EXISTING). The program runs a source STRING
through `timeit.timeit`, and the string replaces the submodule attribute `zu75a.b` with the sibling module
zu75a.c, so `cd <tree root> && python <this file>` prints "result 2". pycsl never reads the string (a plain
`exec` of it is refused by the rebound-name rule); main L21 PROVED the claim below. REFUSED:
PYCSL-SEM-IMPORT-STATE-MANIPULATED (route #326's list gains `timeit`, u75).
"""
# pycsl-expected: FAIL
import zu75a.b
import timeit

timeit.timeit("import zu75a, zu75a.c; zu75a.b = zu75a.c", number=1)


#@ ensures \result == 1
def g() -> int:
    return zu75a.b.one()


if __name__ == "__main__":
    print("result", g())
