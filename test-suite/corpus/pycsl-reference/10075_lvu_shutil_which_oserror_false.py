r"""Test 10075 -- lvU `shutil.which` (expected FAIL): with PATH unset `shutil.which` reads
`os.confstr("CS_PATH")`, which raises the errno's OSError, so `no_exception \all` is false
(the driver's child process, run without PATH, makes `confstr` fail from a profile hook; CPython then raises OSError). Measured verdict:
refused by the `no_exception` callee census (route #161), as lvQ's 9708. Control: 10070.
"""
# pycsl-expected: FAIL
import shutil
from typing import Optional


#@ assigns \nothing
#@ no_exception \all
def where(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


_CHILD = r"""
import importlib.util
import os
import sys
spec = importlib.util.spec_from_file_location("w", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def hook(fr, ev, a):
    if ev == "c_call" and getattr(a, "__name__", "") == "confstr":
        raise OSError(22, "Invalid argument")
sys.setprofile(hook)
try:
    print("result", m.where("sh"))
except OSError:
    print("VIOLATION OSError")
"""


if __name__ == "__main__":
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-I", "-c", _CHILD, __file__], capture_output=True,
                       text=True, env={})
    print(r.stdout.strip() or r.stderr.strip())
