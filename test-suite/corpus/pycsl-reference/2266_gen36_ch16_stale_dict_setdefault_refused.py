r"""Test 2266 — gen #36 ch16 (expected FAIL): the review's `stale_dict` in Python form, the
S-D gate (`inplace-mutator-wall-response.md` §5). `e = self.d` aliases the dict;
`self.d.setdefault("a", "b")` inserts through the other name, so CPython's `e.get("a")` is
`"b"` and `\result == None` is FALSE. A dict is a PURE map in the model, so a lowering of
`setdefault` would let the alias go stale and PROVE the claim; it must stay REFUSED (and
ch16 measured the map carrier's alias hazard to be open at base for `.add`/stores — see
`inplace-mutator-wall-impl.md` S-A/S-D RESULT). This file is `pycsl-expected: FAIL`: the
refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Box:
    d: Dict[str, str] = field(default_factory=dict)

    #@ ensures \result == None
    #@ assigns self.d
    def go(self) -> Optional[str]:
        e = self.d
        self.d.setdefault("a", "b")
        return e.get("a")


if __name__ == "__main__":
    assert Box().go() == "b"
