from __future__ import annotations
import argparse
from pathlib import Path


#@ ensures \result == 0 or \result == 3
#@ assigns \nothing
def cli(p: Path) -> int:
    x = 0
    q = p / "u44"
    try:
        a = argparse.ArgumentParser()
        x = 3
        q.mkdir(parents=True, exist_ok=True)
    except AttributeError:
        return x
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    import tempfile
    r = cli(Path(tempfile.mkdtemp()))
    print("VIOLATION contract" if r not in (0, 3) else "result", r)
