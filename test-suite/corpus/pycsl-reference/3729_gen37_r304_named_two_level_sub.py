r"""Test 3729 -- gen #37 route #304 (expected FAIL): `no_exception ValueError` + own raise of `B(A)`, `A(ValueError)` (two-level user hierarchy). Before #304 the emitter added `raises { B }` to the function's own `let`, so the `no_exception` claim and the `ensures` were checked on normal return only and the file PROVED while CPython raises; now the own raise is a reachability obligation (`no_exception: own raise B reachable`) and FAILS.
"""
# pycsl-expected: FAIL
class A(ValueError):
    pass


class B(A):
    pass

#@ no_exception ValueError
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise B()
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
