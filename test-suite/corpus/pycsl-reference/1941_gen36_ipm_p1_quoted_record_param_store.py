r"""Test 1941 — gen #36 (expected PASS): W-IPM prerequisite P1 — a QUOTED forward-reference
record parameter annotation (`other: "Box"`) is the record, exactly like the bare `Box`.

At 397ada4f the quoted spelling typed `other` as `int` (`_record_param_classes` empty), so the
field store `other.v = ...` and the `\old(other.v)` postcondition could not be stated against a
record at all (Why3 type error). The unquoted spelling (under `from __future__ import
annotations`) was already the record. Twin: 1942 (false claim, must FAIL).
"""
# pycsl-expected: PASS
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Box:
    v: int = 0

    #@ ensures other.v == \old(other.v) + 1
    #@ ensures \result == other.v
    #@ assigns other.v
    def bump(self, other: "Box") -> int:
        other.v = other.v + 1
        return other.v
