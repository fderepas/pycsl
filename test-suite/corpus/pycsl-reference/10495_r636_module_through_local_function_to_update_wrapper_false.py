r"""Test 10495 -- run #9 u75, route #636 (FAIL). The package module object is passed to a PROGRAM function
`h(x)`, whose body hands its parameter to `functools.update_wrapper(x, _Src, assigned=("b",), updated=())`:
the submodule attribute `zu75f.b` becomes the class K, so `cd <tree root> && python <this file>` prints
"result 2". The store happens in the standard library; main L21 PROVED the claim below. REFUSED:
PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M: any value use of a module object, a program callee included).
"""
# pycsl-expected: FAIL
import zu75f.b
import functools

class K:
    @staticmethod
    def one() -> int:
        return 2


class _Src:
    b = K


def h(x: object) -> None:
    functools.update_wrapper(x, _Src, assigned=("b",), updated=())


h(zu75f)


#@ ensures \result == 1
def g() -> int:
    return zu75f.b.one()


if __name__ == "__main__":
    print("result", g())
