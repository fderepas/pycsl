r"""Test 2160 — ch13 seam S-c (expected PASS): `p.resolve()` on a `Path` parameter. In the #31
PATH MODEL a `pathlib.Path` is a Why3 `string`; at base the generic dotted-call fallback minted a
receiver-less `val p_resolve_0 () : int`, so binding it to a `Path`-typed local or returning it
from a `-> Path` function was an L3-tc error (an int where a string is expected). It now lowers to
the impure `path_resolve_op (s: string) : string`, so the result is a path and the surrounding
value claims are checked. Twins: 2161, 2162.
"""
# pycsl-expected: PASS
from pathlib import Path


#@ ensures \result == n + 1
#@ assigns \nothing
def bump_after_resolve(p: Path, n: int) -> int:
    r: Path = p.resolve()
    nm = r.name
    return n + 1


#@ ensures \result == q
#@ assigns \nothing
def keep_other(p: Path, q: Path) -> Path:
    r = p.resolve()
    if r == q:
        return r
    return q
