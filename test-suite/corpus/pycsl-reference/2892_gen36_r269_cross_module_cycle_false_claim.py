r"""Test 2892 — route #269 R5 (expected FAIL): `g` (here) calls the imported
`multi_file_lib.r269_main_peer.f`, which calls back into the running program's `g` through
`__main__` — a call cycle across the MODULE boundary with no termination argument. The
import is a trusted stub carrying `f`'s `ensures`, so `\result == 0` PROVED at 8b0bfbbd,
assuming `f` circularly. CPython: RecursionError. The call graph now reads the imported
body's calls back into this unit; refused (PYCSL-SEM-CROSS-MODULE-RECURSION).
"""
# pycsl-expected: FAIL
from multi_file_lib.r269_main_peer import f

#@ ensures \result == 0
#@ assigns \nothing
def g(k: int) -> int:
    return f(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(g(1))
    except RecursionError:
        print("RecursionError")
