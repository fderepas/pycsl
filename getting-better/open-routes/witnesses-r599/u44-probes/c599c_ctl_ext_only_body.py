from __future__ import annotations
from pathlib import Path


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def f(p: Path, q: Path) -> int:
    x = 0
    try:
        p.mkdir(parents=True, exist_ok=True)
        x = 1
        q.mkdir(parents=True, exist_ok=True)
    except FileNotFoundError:
        return x
    return 0


if __name__ == "__main__":
    import tempfile
    d = tempfile.mkdtemp()
    r = f(Path(d) / "a", Path(d) / "b")
    print("VIOLATION contract" if r not in (0, 1) else "result", r)
