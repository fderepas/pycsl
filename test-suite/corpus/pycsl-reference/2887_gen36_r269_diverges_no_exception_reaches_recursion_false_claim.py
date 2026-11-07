r"""Test 2887 — route #269 R4 (expected FAIL): `top` is `#@ \diverges` + `#@ no_exception
\all` and is NOT itself recursive — it calls `f`, an unbounded `#@ \diverges` recursion.
The RecursionError raised in `f` escapes `top`. CPython: RecursionError. A `\diverges`
function under `no_exception \all` may not REACH a call cycle; refused
(PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION).
"""
# pycsl-expected: FAIL
#@ ensures \result == 0
#@ assigns \nothing
#@ \diverges
def f(k: int) -> int:
    return f(k)

#@ ensures \result == 0
#@ assigns \nothing
#@ \diverges
#@ no_exception \all
def top(k: int) -> int:
    return f(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(top(1))
    except RecursionError:
        print("RecursionError")
