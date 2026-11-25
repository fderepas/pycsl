r"""Test 10493 -- run #9 u75, review rt83 u1, route #636 (FAIL, PRE-EXISTING). The program hands the package
MODULE OBJECT to `functools.update_wrapper(zu75d, _Src, assigned=("b",), updated=())`, which runs
`setattr(zu75d, "b", _Src.b)` inside the standard library and replaces the submodule attribute `zu75d.b`
with the class K, so `cd <tree root> && python <this file>` prints "result 2". No store of the program is
seen; main L21 PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M).
"""
# pycsl-expected: FAIL
import zu75d.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


functools.update_wrapper(zu75d, _Src, assigned=("b",), updated=())


#@ ensures \result == 1
def g() -> int:
    return zu75d.b.one()


if __name__ == "__main__":
    print("result", g())
