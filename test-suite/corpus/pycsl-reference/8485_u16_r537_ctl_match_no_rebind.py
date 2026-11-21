r"""Test 8485 -- route #537 (control, expected PASS): a `match` whose patterns capture no parameter keeps the parameters at their declared kinds: `match s: case "a": ...` then `n * n` over an int parameter; CPython f(3, "a") returns 1
"""
# pycsl-expected: PASS


class C:
    def __init__(self, n: int, s: str) -> None:
        self.t = 0
        match s:
            case "a":
                self.t = 1
            case _:
                self.t = 2
        self.k = n * n


#@ no_exception \all
#@ ensures \result == 1
def f(n: int, s: str) -> int:
    c = C(n, s)
    return 1


if __name__ == "__main__":
    print(f(3, "a"))
