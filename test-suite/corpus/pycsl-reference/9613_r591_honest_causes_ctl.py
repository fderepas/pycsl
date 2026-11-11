r"""Test 9613 -- route #591 CONTROL (expected PASS, the advice of PYCSL-R591 followed): `from None` (also inside a handler) and `from <ExceptionClass>` are exception causes (`from e` of the enclosing handler's own name is accepted by this rule, but every read of `e` is route #233's refusal); each raise is caught and counted.
"""
# pycsl-expected: PASS
class E(Exception):
    pass


#@ no_exception \all
#@ ensures \result == k + 3
def f(k: int) -> int:
    r = k
    try:
        raise E("a") from None
    except E:
        r = r + 1
    try:
        raise E("b") from ValueError
    except E:
        r = r + 1
    try:
        try:
            raise ValueError("v")
        except ValueError:
            raise E("c") from None
    except E:
        r = r + 1
    return r


if __name__ == "__main__":
    print(f(2))
