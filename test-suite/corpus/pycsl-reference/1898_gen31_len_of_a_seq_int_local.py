r"""Test 1898 — gen #31 WITNESS (expected PASS): `len()` of a `seq int` local.

A list local bound from a `Dict[K, List[int]]` read is a `seq int`. `statements.py` ~5900
promotes a SINGLE-assign list local to `_seq_locals` — the set whose `len()` lowers to
`Seq.length` — only when its element type is `string` (or `emit_ir`, and that one is
file-gated), so a `seq int` local kept the ARRAY model and `len` fell through to
`Array.length`:

    This expression has type seq.Seq.seq int, but is expected to have type int

THE 2x2 THAT LOCATED IT, all four identical but for one annotation:

    Dict[str, List[str]]   SUCCESS        Dict[str, List[int]]   FAILED
    Dict[int, List[str]]   SUCCESS        Dict[int, List[int]]   FAILED

The KEY type is irrelevant, and so is the declaration site — a `@dataclass` class-body
field behaves exactly like this `__init__` AnnAssign, and `0746.py` is the corpus's working
`Dict[str, List[str]]` instance. The ELEMENT type was the whole discriminator.

Third instance in this generation of one rule implemented for the element type the first
witness happened to have; the other two were `needs_array` and its `needs_seq` twin.
"""
# pycsl-expected: PASS
from typing import Dict, List


def mutable_state(cls):
    return cls


_ = 0  # anchor


@mutable_state
class C:
    def __init__(self) -> None:
        self.m: Dict[int, List[int]] = {}

    #@ ensures \result >= 0
    def arity(self, k: int) -> int:
        fp = self.m.get(k, [])
        return len(fp)
