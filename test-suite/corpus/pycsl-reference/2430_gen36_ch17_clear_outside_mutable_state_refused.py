r"""Test 2430 — gen #36 ch17 S-D (expected FAIL): BOUNDARY: outside `@mutable_state` the clear arm does not fire; `self.d.clear()` keeps the
generic in-place-mutator refusal (claim TRUE, CPython 0 — refused, not proved).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ ensures \result == 0
    #@ assigns self.d
    def m(self) -> int:
        self.d[1] = 5
        self.d.clear()
        return 1 if 1 in self.d else 0


if __name__ == "__main__":
    assert C().m() == 0
