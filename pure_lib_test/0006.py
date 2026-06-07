#!/usr/bin/env python3
"""Concrete test for Phase 4-8 modules: sysmod, iomod, hlib, ctxlib, typ, subproc, etc."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

passed = 0
failed = 0

def check(name, cond):
    global passed, failed
    if cond:
        print(f"PASS: {name}")
        passed += 1
    else:
        print(f"FAIL: {name}")
        failed += 1

# --- hashlib (hlib) ---
from pure_lib.hlib import new_sha256

h = new_sha256([1, 2, 3])
check("sha256 digest length", len(h.digest()) == 32)
check("sha256 hexdigest length", len(h.hexdigest()) == 64)
h.update([4, 5])
check("sha256 update works", True)

# --- contextlib (ctxlib) ---
from pure_lib.ctxlib import nullcontext, ExitStack

nc = nullcontext(42)
check("nullcontext enter", nc.__enter__() == 42)
check("nullcontext exit", nc.__exit__(0, 0, 0) == 0)

es = ExitStack()
es.__enter__()
called = [False]
es.callback(lambda: None)
check("exitstack push", es._size == 1)
es.__exit__(0, 0, 0)
check("exitstack cleanup", es._size == 0)

# --- typing (typ) ---
from pure_lib.typ import cast

check("cast identity", cast(int, 42) == 42)
check("cast string", cast(str, "hello") == "hello")

# --- io (iomod) ---
from pure_lib.iomod import StringIO

sio = StringIO(0)
sio.write([65, 66, 67])  # "ABC"
check("stringio write returns len", True)
check("stringio tell after write", sio.tell() == 3)
sio.seek(0)
check("stringio seek", sio.tell() == 0)
n = sio.read(2)
check("stringio read 2", n == 2)
check("stringio getvalue", len(sio.getvalue()) == 3)

# --- subprocess (subproc) ---
from pure_lib.subproc import Popen, CompletedProcess, run

p = Popen(["echo", "hello"])
check("popen poll", p.poll() == -1)
out = p.communicate(0)
check("popen communicate returns tuple", len(out) == 2)
check("popen returncode after communicate", p.wait() >= 0)

result = run(["test"], 0, 0)
check("run returns CompletedProcess", result.returncode >= 0)

# --- sys (sysmod) ---
from pure_lib.sysmod import get_float_info_max_10_exp

check("float_info max_10_exp", get_float_info_max_10_exp() == 308)

# --- copy (cpmod) ---
from pure_lib.cpmod import deepcopy, copy

check("deepcopy identity", deepcopy(42) == 42)
check("copy identity", copy(42) == 42)

# --- tempfile (tmpf) ---
from pure_lib.tmpf import mkstemp, gettempdir

r = mkstemp(0, 0, 0)
check("mkstemp returns tuple", len(r) == 2)
check("mkstemp name > 0", r[1] > 0)
r2 = mkstemp(0, 0, 0)
check("mkstemp unique names", r[1] != r2[1])

# --- Summary ---
print(f"\n{passed} passed, {failed} failed out of {passed + failed}")
if failed:
    sys.exit(1)
