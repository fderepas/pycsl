r"""Test 5104 -- gen #37 route #226 increment 2c (expected FAIL): a PARAMLESS constructor storing `[0] * 3` under `\length(self.disk) == 4`; `#@ no_exception \all` on `self.disk[3]` PROVED at base (no goal for a `\length` invariant). CPython `C().last()` raises IndexError. 2c states the literal length Module 5 records: `forall disk : array int. (Array.length disk) = 3 -> ((Array.length disk) = 4)`, which FAILS.
"""
# pycsl-expected: FAIL


#@ class invariant \length(self.disk) == 4
class C:
    def __init__(self) -> None:
        self.disk: list = [0] * 3

    #@ no_exception \all
    #@ assigns \nothing
    def last(self) -> int:
        return self.disk[3]


if __name__ == "__main__":
    try:
        C().last()
        raise SystemExit("expected IndexError")
    except IndexError:
        print("IndexError")
