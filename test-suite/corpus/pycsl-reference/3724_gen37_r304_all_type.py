r"""Test 3724 -- gen #37 route #304 (expected FAIL): `no_exception \all` + own `raise TypeError` (outside the tracked Phase-1 set). Before #304 the emitter added `raises { TypeError }` to the function's own `let`, so the `no_exception` claim and the `ensures` were checked on normal return only and the file PROVED while CPython raises; now the own raise is a reachability obligation (`no_exception: own raise TypeError reachable`) and FAILS.
"""
# pycsl-expected: FAIL

#@ no_exception \all
#@ ensures \result == 0
def g(x: int) -> int:
    if x < 0:
        raise TypeError("neg")
    return 0

if __name__ == "__main__":
    assert g(-1) == 0
