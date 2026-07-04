"""Test 0776 — cleared-hash.md S4/S7: NEGATIVE driver on a record dict FIELD (false claim stays unprovable).

A control on the faithful field model: distinct keys hold INDEPENDENT values, so `self.d["a"] ==
self.d["b"]` is genuinely FALSE after writing them different values. The verifier must NOT prove it
(a `map string` field model that proved this would be unsound / vacuous). Expected UNPROVEN — the
non-aliasing that makes 0772/0773/0774 provable is exactly what makes this false claim unprovable."""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Store:
    d: Dict[str, int] = None

    #@ requires True
    #@ ensures \result == 0
    #@ assigns self.d
    #@ no_exception KeyError
    def values_differ_field(self) -> int:
        self.d = {}
        self.d["a"] = 1
        self.d["b"] = 2
        # FALSE: self.d["a"] (=1) != self.d["b"] (=2); the claim \result == 0 via this
        # equality cannot hold.
        if self.d["a"] == self.d["b"]:
            return 0
        return 1
