r"""Test 2886 — route #269 R4 (expected FAIL): 2885 as a module-level `let rec`: `f` is
`#@ \diverges` + `#@ no_exception \all` and calls itself without end. PROVED at 8b0bfbbd (and
at 283d1033). CPython: RecursionError. Now refused
(PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION).
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ assigns \nothing
#@ \diverges
#@ no_exception \all
def f(k: int) -> int:
    return f(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(f(1))
    except RecursionError:
        print("RecursionError")
