r"""Test 2000 — gen #36 (expected PASS): a LOCAL `List[str]` accumulator grown only by
`acc.extend(self.<m>(..))`, where `<m>` is declared `-> List[str]`. At base the `.extend`
reached the in-place-mutator REFUSAL (no lowering took the receiver); now `acc` is a
`seq string` local and each `.extend` is `acc := Seq.(++) !acc (snapshot_str <call>)`
(length- and element-preserving), and `if acc:` is `Seq.length !acc <> 0`. Both extends are
counted, so the length is proved to be 2 + 2. Twin: 2001 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List


class Collector:
    def __init__(self) -> None:
        self.n = 0

    #@ \trusted
    #@ ensures len(\result) == 2
    #@ assigns \nothing
    def norm(self, xs: List[str]) -> List[str]:
        return ["x", "y"]

    #@ ensures \result == 4
    #@ assigns \nothing
    def gather(self, xs: List[str], ys: List[str]) -> int:
        acc: List[str] = []
        acc.extend(self.norm(xs))
        acc.extend(self.norm(ys))
        if acc:
            return len(acc)
        return 0
