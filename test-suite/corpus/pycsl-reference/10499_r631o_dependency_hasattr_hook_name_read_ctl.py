r"""Test 10499 -- run #9 u75, review rt83 o7 (u73 INTRODUCED over-refusal, PASS). A reached dependency READS
the name `__getattr__` with `hasattr(x, "__getattr__")`: no hook is bound; `cd <tree root> && python <this
file>` prints "result 4" and pycsl proves it (u73 refused it with PYCSL-SEM-IMPORT-MODULE-HOOK).
"""
# pycsl-expected: PASS
import zu75j.b
from zu75j_probe import three


#@ ensures \result == 4
def g() -> int:
    return zu75j.b.one() + three()


if __name__ == "__main__":
    print("result", g())
