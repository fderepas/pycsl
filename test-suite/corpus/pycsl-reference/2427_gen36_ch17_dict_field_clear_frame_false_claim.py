r"""Test 2427 — gen #36 ch17 S-D (expected FAIL): FRAME: `self.d.clear()` under `#@ assigns \nothing` is a write the contract does not
declare; the store goes through the field-store lowering, so Why3 rejects the unlisted write.
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

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self) -> int:
        self.d[1] = 5
        self.d.clear()
        return 1 if 1 in self.d else 0


if __name__ == "__main__":
    assert C().m() == 0
