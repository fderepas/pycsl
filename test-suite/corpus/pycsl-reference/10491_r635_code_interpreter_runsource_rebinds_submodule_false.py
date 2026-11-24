r"""Test 10491 -- run #9 u75, review rt83 s3, route #635 (FAIL, PRE-EXISTING). The program runs a source STRING
through `code.InteractiveInterpreter().runsource`, which replaces the submodule attribute `zu75b.b` with
zu75b.c, so `cd <tree root> && python <this file>` prints "result 2"; main L21 PROVED the claim below.
REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (route #326's list gains `code`, u75).
"""
# pycsl-expected: FAIL
import zu75b.b
import code

code.InteractiveInterpreter().runsource("import zu75b, zu75b.c; zu75b.b = zu75b.c")


#@ ensures \result == 1
def g() -> int:
    return zu75b.b.one()


if __name__ == "__main__":
    print("result", g())
