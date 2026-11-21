r"""Test 2296 — gen #36 r243 (expected FAIL): route #243 witness `field_alias1`: `self.g = self.d` makes ONE dict reachable through two
fields; `self.d[1] = 5` is then visible through `self.g`. CPython returns True; the claim
`\result == False` PROVED at cdac19a6 (the model's `self.g` was a COPY) and the field store is
now REFUSED (PYCSL-WHYML-COLLECTION-ALIAS).
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

    #@ ensures \result == False
    #@ assigns self.d, self.g
    def m(self) -> bool:
        self.d = {}
        self.g = self.d
        self.d[1] = 5
        return 1 in self.g


if __name__ == "__main__":
    assert C().m() is True
