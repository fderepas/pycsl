r"""Test 2946 — gen #36 r272 (expected FAIL): a CHAIN through a MODULE function: `m -> f -> C().chk`. `f` is applied concretely, but
its exception arrives through a method stub, so its emission carries no `raises` and Why3's
effect typing never sees it. PROVED `no_exception \all` at 5fe6cbdd; CPython raises ValueError.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    def chk(self, k: int) -> int:
        if k > 0:
            raise ValueError("bad")
        return 0


def f(k: int) -> int:
    return C().chk(k)


#@ ensures \result == 7
#@ no_exception \all
def m(k: int) -> int:
    f(k)
    return 7


if __name__ == "__main__":
    try:
        m(1)
        raise SystemExit("no exception")
    except ValueError:
        print("ValueError raised: the no_exception claim is false")
