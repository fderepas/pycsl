r"""Test 10456 -- run #9 u72, review rt80 R3b, route #630 (FAIL, PRE-EXISTING). qi72.C.m returns qi72's own
`helper()` (1). The program defines its own `helper` (2) and a module-level `obj = C()`, so `obj.m()` is
inlined. The class resolver skipped qi72's helper (name taken) and the inlined body called the program's
helper: `g() == 2` PROVED at L20. CPython prints "result 1". Now qi72's helper keeps its own identity
(a fresh name) and the inlined body calls it: the claim fails.
"""
# pycsl-expected: FAIL
from qi72 import C


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


obj = C()


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return obj.m()


if __name__ == "__main__":
    print("result", g())
