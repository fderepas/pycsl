r"""Test 9961 -- route #599 / PATH-RECEIVER control (expected PASS): the `.mkdir(..)` receiver is bound from `<Path parameter> / <str>` before the `try`, the argparse constructor covers `except AttributeError` and the mkdir covers `except OSError`: every operation of the body is an ext-modelled call; the handler returns the value stored before it (3) or 0
"""
# pycsl-expected: PASS
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
