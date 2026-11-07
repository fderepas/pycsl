r"""Test 2424 — gen #36 ch17 S-D (expected FAIL): STALE-ALIAS attempt: `a = self.d; self.d.clear(); return 1 in a`. CPython: `a` IS the
cleared dict (0). The pure-map carrier would keep `a` as a stale COPY and prove `\result == 1`
(spike `ipm/ch17/spike_ds.mlw` f2); route #59's local-alias guard (mutator calls are stores)
must REFUSE it.
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

    #@ ensures \result == 1
    #@ assigns self.d
    def m(self) -> int:
        self.d[1] = 5
        a = self.d
        self.d.clear()
        return 1 if 1 in a else 0


if __name__ == "__main__":
    assert C().m() == 0
