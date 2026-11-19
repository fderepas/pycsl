r"""Test 5112 -- gen #37 route #226 increment 2c CONTROL (expected PASS): 5104 with the TRUE length, `self.disk = [0] * 4` under `\length(self.disk) == 4`; `#@ no_exception \all` on `self.disk[3]`. `(Array.length disk) = 4 -> ((Array.length disk) = 4)` PROVES. CPython `C().last()` is 0.
"""


#@ class invariant \length(self.disk) == 4
class C:
    def __init__(self) -> None:
        self.disk: list = [0] * 4

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    assert C().last() == 0
