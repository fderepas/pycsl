r"""Test 2180 — ch14 seam (expected PASS): the `pathlib` filesystem predicates `.is_file()`,
`.is_dir()` and `.exists()` on a COMPOUND `Path` receiver (`d / "f"`, `d.parent`). In the #31
PATH MODEL a `pathlib.Path` is a Why3 `string`; at base the generic dotted-call fallback applied
an opaque `is_file_1 (x: int) : int` to the receiver, so the string-typed path was an L3-tc
error and the whole file was refused. They now lower to the impure `os.path` predicate ops
(`path_isfile_op` / `path_isdir_op` / `path_exists_op : string -> int`), so the value claim
below is checked. CPython: `probe_dir(Path("/tmp"), 4) == 5` whatever the filesystem holds.
Twins: 2181, 2182, 2183 (false claims), 2184 (simple-name control).
"""
# pycsl-expected: PASS
from pathlib import Path


#@ ensures \result == n + 1
#@ assigns \nothing
def probe_dir(d: Path, n: int) -> int:
    has_lake = (d / "lakefile.lean").is_file() and d.parent.is_dir()
    if (d / "x").exists() or has_lake:
        return n + 1
    return n + 1
