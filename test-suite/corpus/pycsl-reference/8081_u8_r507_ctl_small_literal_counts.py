r"""Test 8081 -- routes #507 / #508 / #509 (control, expected PASS): repetition / multiplication by a small int LITERAL inside displays (`"ab" * 3`, `s * 2`, `[0] * 4`, `n * 2`, `3 * n`): no index-sized conversion of a huge count; CPython f(10**20, 'ab') returns 1
"""
# pycsl-expected: PASS
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, s: str) -> int:
    v = {"ab" * 3, s * 2}
    w = (1, [0] * 4)
    u = len([n * 2, 3 * n])
    return 1


if __name__ == "__main__":
    print("result", f(10**20, "ab"))
