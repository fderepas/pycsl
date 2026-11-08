r"""Test 2184 — ch14 seam (expected PASS, faithfulness control): a predicate on a SIMPLE-NAME
`Path` receiver (`p.exists()`), which already type-checked at base as the receiver-less
`val p_exists_0 () : int`; it now carries its receiver (`path_exists_op p`). The branch value
claim must keep proving and must not depend on the predicate's answer. CPython:
`twice(Path("/tmp"), 3) == 6`, `twice(Path("/nonexistent"), 3) == 6`.
"""
# pycsl-expected: PASS
from pathlib import Path


#@ ensures \result == 2 * n
#@ assigns \nothing
def twice(p: Path, n: int) -> int:
    if p.exists():
        return n + n
    return 2 * n
