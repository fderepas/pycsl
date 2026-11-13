r"""Test 9709 -- lvQ open-world model (expected FAIL, refused PYCSL-R7Q-EXT-HANDLE-ESCAPES): the
CompletedProcess is returned, so it is not a process local and the law-free handle cannot
represent it.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import subprocess


#@ ensures True
#@ assigns \nothing
def run(cmd: str) -> int:
    r = subprocess.run([cmd], capture_output=True, text=True)
    return r


if __name__ == "__main__":
    print("result", run("true"))
