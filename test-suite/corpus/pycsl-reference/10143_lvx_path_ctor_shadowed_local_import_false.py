r"""Test 10143 -- lvX `Path(<str>)` model, route #610 control (expected FAIL): a function-local
import binds `Path` to `tempfile.mkdtemp`, shadowing the module-level `from pathlib import Path`,
so `Path(s)` creates a fresh directory (suffix `s`) on each call. The model applies only when
`Path` is the pathlib import bound nowhere in the function; here it gets NO model (refused or the
old generic lowering), so the determinism claim `\result == True` must NOT prove (CPython: two
different directories, False).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    from tempfile import mkdtemp as Path
    return Path(s) == Path(s)


if __name__ == "__main__":
    r = same("-lvx-10143")
    print("VIOLATION contract" if r is not True else "result", r)
