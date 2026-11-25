r"""Test 10494 -- run #9 u75, review rt83 v2, route #636 (FAIL, PRE-EXISTING). The program hands the SUBMODULE
object `zu75e.b` to `functools.update_wrapper(zu75e.b, K, assigned=("one",), updated=())`, which replaces
the dependency function `zu75e.b.one` with `K.one` (returns 2), so `cd <tree root> && python <this file>`
prints "result 2"; main L21 PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M).
"""
# pycsl-expected: FAIL
import zu75e.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


functools.update_wrapper(zu75e.b, K, assigned=("one",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zu75e.b.one()


if __name__ == "__main__":
    print("result", g())
