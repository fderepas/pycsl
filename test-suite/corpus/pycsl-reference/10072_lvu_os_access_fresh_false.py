r"""Test 10072 -- lvU `os.access` (expected FAIL): each call is a FRESH query (the file's mode can
change between them), so the claim that a second call agrees with the first is not provable.
CPython answers differently when the mode changes between the calls (the driver's child process
runs a `chmod` there from a profile hook).
Control: 10070.
"""
# pycsl-expected: FAIL
import os


#@ ensures \result == 0
#@ assigns \nothing
def flip(p: str) -> int:
    if os.access(p, os.X_OK) and not os.access(p, os.X_OK):
        return 1
    return 0


_CHILD = r"""
import importlib.util
import os
import sys
spec = importlib.util.spec_from_file_location("w", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
import tempfile
fd, p = tempfile.mkstemp()
os.close(fd)
os.chmod(p, 0o700)
def hook(fr, ev, a):
    if ev == "c_return" and getattr(a, "__name__", "") == "access":
        os.chmod(p, 0o600)
sys.setprofile(hook)
r = m.flip(p)
sys.setprofile(None)
os.unlink(p)
print("VIOLATION contract" if r != 0 else "result", r)
"""


if __name__ == "__main__":
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-I", "-c", _CHILD, __file__], capture_output=True,
                       text=True, env={})
    print(r.stdout.strip() or r.stderr.strip())
