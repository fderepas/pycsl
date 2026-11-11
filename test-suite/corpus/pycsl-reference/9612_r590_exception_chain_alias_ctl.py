r"""Test 9612 -- route #590 CONTROL (expected PASS): a user exception derived through a user base (`E(B)`, `B(Exception)`), raised through a class alias and bare, and a builtin exception are raised and caught by their own names.
"""
# pycsl-expected: PASS
class B(Exception):
    pass


class E(B):
    pass


A = E


#@ no_exception \all
#@ ensures \result == 2 * k + 3
def f(k: int) -> int:
    r = 0
    try:
        raise A("a")
    except A:
        r = r + k + 1
    try:
        raise E
    except E:
        r = r + k
    try:
        raise ValueError("v")
    except ValueError:
        r = r + 2
    return r


if __name__ == "__main__":
    print(f(5))
