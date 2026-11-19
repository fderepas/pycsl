r"""Test 10070 -- lvU `os.access` / `shutil.which` CONTROL (expected PASS): `os.access(<str>,
<mode>)` is an impure LAW-FREE world query (a fresh value per call, raising ValueError /
UnicodeEncodeError on a NUL / unencodable path, never an OSError), so only what holds for EVERY
answer is provable: here, that the result is 0 or 1. `where` returns `shutil.which(..)`, any
`str` or None. Twins (must FAIL): 10071-10076.
"""
# pycsl-expected: PASS
import os
import shutil
from typing import Optional


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def can_run(p: str) -> int:
    if os.path.isfile(p) and os.access(p, os.X_OK):
        return 1
    return 0


#@ assigns \nothing
def where(cmd: str) -> Optional[str]:
    if os.access(cmd, os.X_OK):
        return cmd
    return shutil.which(cmd)


if __name__ == "__main__":
    for p in ["/bin/sh", "/nonexistent", "/etc/hostname"]:
        r = can_run(p)
        print("VIOLATION contract" if r not in (0, 1) else "result", r, where("sh"))
