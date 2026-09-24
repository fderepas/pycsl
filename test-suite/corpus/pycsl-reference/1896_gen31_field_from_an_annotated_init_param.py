r"""Test 1896 — gen #31 WITNESS (expected PASS): a field assigned from an ANNOTATED
`__init__` PARAMETER keeps the parameter's type.

`Module5_IREmitter._collect_class_fields` infers an unannotated field's type from the RHS
SHAPE alone — Dict literal, Set literal, List literal, or a `set()`/`dict()`/`list()` call.
An `ast.Name` RHS matches none of those, so the single most common way a Python class stores
a typed collection,

    def __init__(self, m: Dict[str, List[str]]) -> None:
        self.m = m

fell through to `"int"` with no `value_type` at all. The annotation is on the PARAMETER
rather than on the assignment, and it is just as binding. Before the repair this file
measured `This expression has type array.Array.array int @rho, but is expected …` — a Why3
type error naming nothing the user wrote, for a class that merely holds a dict of lists.

The ANNOTATED sibling branch (`self.m: Dict[str, List[str]] = m`) already did the right
thing, which is why this went unnoticed: the same program, one annotation moved, verifies.
"""
# pycsl-expected: PASS
from typing import Dict, List


def mutable_state(cls):
    return cls


_ = 0  # anchor


@mutable_state
class C:
    def __init__(self, m: Dict[str, List[str]]) -> None:
        self.m = m

    #@ ensures \result >= 0
    def arity(self, name: str) -> int:
        fp = self.m.get(name, [])
        return len(fp)
