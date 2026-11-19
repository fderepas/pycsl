r"""Test 2161 — ch13 seam S-c (expected FAIL): `Path.resolve()` is NOT the identity. CPython:
`Path("a").resolve()` is the ABSOLUTE `<cwd>/a`, which is not `Path("a")`. The model's
`path_resolve_op` carries no content law (it reads the cwd and the filesystem), so the claim
`\result == p` must stay unproved. Control: 2160.
"""
# pycsl-expected: FAIL
from pathlib import Path


#@ ensures \result == p
#@ assigns \nothing
def resolved(p: Path) -> Path:
    return p.resolve()
