r"""Test 5272 -- gen #37 route #384 (control, expected PASS): `[]` then `append(7)` under `\length(self.disk) >= 1`, `no_exception` on `self.disk[0]`. PROVED.
"""
# pycsl-expected: PASS
from typing import List


def mutable_state(cls):
    return cls


#@ class invariant \length(self.disk) >= 1
@mutable_state
class D:
    def __init__(self) -> None:
        self.disk: List[int] = []
        self.disk.append(7)

    #@ no_exception \all
    #@ assigns \nothing
    def first(self) -> int:
        return self.disk[0]


if __name__ == "__main__":
    print(D().first())
