r"""Test 2302 — gen #36 r243 (expected FAIL): route #243: the alias made in `__post_init__`, which Module 5 drops. CPython returns True;
PROVED at cdac19a6, now REFUSED by the constructor scan in `_run_pipeline`
(PYCSL-SEM-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)
    g: Dict[int, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.g = self.d

    #@ ensures \result == False
    #@ assigns self.d
    def m(self) -> bool:
        if 1 in self.g:
            return False
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    assert C().m() is True
