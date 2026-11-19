r"""Test 2310 — gen #36 r243 (expected PASS): routes #243/#244 CONTROL: a dict field stored through with NO alias anywhere keeps proving
(CPython: True).
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ ensures \result == True
    #@ assigns self.d
    def m(self) -> bool:
        self.d[1] = 5
        return 1 in self.d


if __name__ == "__main__":
    assert C().m() is True
