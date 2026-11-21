r"""Test 3730 -- gen #37 route #304 (expected FAIL): METHOD form -- `no_exception \all` + own `raise ValueError` in a method body. Before #304 the method's own `let` got `raises { ValueError }` and the file PROVED while CPython raises; now the own raise is a reachability obligation and FAILS.
"""
# pycsl-expected: FAIL


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ no_exception \all
    #@ ensures \result == 0
    def m(self, x: int) -> int:
        if x < 0:
            raise ValueError("neg")
        return 0

if __name__ == "__main__":
    assert C().m(-1) == 0
