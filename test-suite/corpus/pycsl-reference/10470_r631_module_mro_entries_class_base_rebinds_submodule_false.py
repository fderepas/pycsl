r"""Test 10470 -- run #9 u73, review rt81 p2, route #631 (FAIL, PRE-EXISTING). The program uses the package
module zu73a as a CLASS BASE (`class C(zu73a)`); PEP 560 makes CPython call zu73a's module-level
`__mro_entries__(bases)` with the module object itself in `bases`, and it stores `setattr(bases[0], "b", K)`,
replacing the submodule attribute `zu73a.b`, so `cd <tree root> && python <this file>` prints "result 2".
L19 c115e0a5a and the V2D batch head 08e65645c PROVED the claim below (the class base was an exempt position
and route #483 does not judge the program). REFUSED: PYCSL-SEM-IMPORT-MODULE-HOOK (u73).
"""
# pycsl-expected: FAIL
import zu73a.b


class C(zu73a):
    pass


#@ ensures \result == 1
def g() -> int:
    return zu73a.b.one()


if __name__ == "__main__":
    print("result", g())
