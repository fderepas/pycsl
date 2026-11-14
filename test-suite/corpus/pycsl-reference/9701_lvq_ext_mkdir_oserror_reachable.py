r"""Test 9701 -- lvQ open-world model (expected FAIL): `mkdir` may raise any OSError (here a
FileExistsError when the path is a file), so the `except OSError` arm is reachable and
`\result == 0` must NOT prove. Twin of 9700.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import tempfile
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def make(p: Path) -> int:
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    f = Path(d) / "f"
    f.write_text("x")
    r = make(f)
    print("VIOLATION contract" if r != 0 else "result", r)
