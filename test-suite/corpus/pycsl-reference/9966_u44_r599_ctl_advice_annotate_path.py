r"""Test 9966 -- route #599 / PATH-RECEIVER advice control (expected PASS): rt58 c01 with the advice of the new PYCSL-R7Q-EXT-PATH-RECEIVER refusal followed -- the receiver is ANNOTATED `Path`, so `.mkdir(..)` cannot raise AttributeError and the handler is reached only from the modelled `argparse.ArgumentParser()` (with x == 0); `\result == 0` holds on every path
"""
# pycsl-expected: PASS
from __future__ import annotations
import argparse
from pathlib import Path


#@ ensures \result == 0
#@ assigns \nothing
def cli(s: Path) -> int:
    x = 0
    try:
        p = argparse.ArgumentParser()
        x = 1
        s.mkdir(parents=True, exist_ok=True)
    except AttributeError:
        return x
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    import tempfile
    r = cli(Path(tempfile.mkdtemp()) / "u44")
    print("VIOLATION contract" if r != 0 else "result", r)
