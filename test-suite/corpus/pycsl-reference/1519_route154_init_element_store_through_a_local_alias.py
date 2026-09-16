r"""Test 1519 - ROUTE #154 carrier-rerun on gen #29's own draft: `xs = self.xs; xs[0] = 9` — the store goes through a LOCAL ALIAS, `C().xs[0] == 1` PROVED at HEAD and on the first draft; CPython 9. A load of `self.<f>` that can hand the container out makes its contents unknown.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]
        xs = self.xs
        xs[0] = 9


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.xs[0]

