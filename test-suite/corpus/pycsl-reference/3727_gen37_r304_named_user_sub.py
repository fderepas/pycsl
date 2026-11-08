r"""Test 3727 -- gen #37 route #304 (expected FAIL): `no_exception ValueError` + own raise of a user subclass `E(ValueError)`. Before #304 the emitter added `raises { E }` to the function's own `let`, so the `no_exception` claim and the `ensures` were checked on normal return only and the file PROVED while CPython raises; now the own raise is a reachability obligation (`no_exception: own raise E reachable`) and FAILS.
"""
# pycsl-expected: FAIL
class E(ValueError):
    pass

#@ no_exception ValueError
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise E()
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
