r"""Test 3095 — route #280 (expected FAIL): `c.me().bump()` — a CALL-RESULT receiver (`me` returns
`self`) — dropped `bump`'s write; `c.v == 0` PROVED at 72ab1c57 (census probe q2). CPython: 1.
Now refused.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def bump(self) -> None:
        self.v = self.v + 1

    #@ assigns \nothing
    def me(self) -> "C":
        return self


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    c.me().bump()
    return c.v


if __name__ == "__main__":
    assert f() == 1
