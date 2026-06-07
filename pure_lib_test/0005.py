#!/usr/bin/env python3
"""Concrete test for all Phase 1+3 modules: tm, bsect, kw, enm, fut, coll, udata."""
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

# --- time (tm) ---
from pure_lib.tm import ClockModel, monotonic

c = ClockModel()
t1 = c.monotonic()
t2 = c.monotonic()
check("clock monotonic increasing", t2 > t1)
check("clock monotonic >= 0", t1 >= 0)

t3 = monotonic()
check("module-level monotonic >= 0", t3 >= 0)

# --- bisect (bsect) ---
from pure_lib.bsect import bisect_left

a = [1, 3, 5, 7, 9]
check("bisect_left existing", bisect_left(a, 5, 0, 5) == 2)
check("bisect_left before all", bisect_left(a, 0, 0, 5) == 0)
check("bisect_left after all", bisect_left(a, 10, 0, 5) == 5)
check("bisect_left between", bisect_left(a, 4, 0, 5) == 2)
check("bisect_left empty range", bisect_left(a, 5, 2, 2) == 2)

# --- keyword (kw) ---
from pure_lib.kw import kwlist

check("kwlist has items", len(kwlist) > 0)
check("kwlist contains if", "if" in kwlist)
check("kwlist contains while", "while" in kwlist)
check("kwlist no garbage", "foobar" not in kwlist)

# --- enum (enm) ---
from pure_lib.enm import IntEnum, auto

e = IntEnum(42, "ANSWER")
check("IntEnum value", e.value() == 42)
check("IntEnum name", e.name() == "ANSWER")

a1 = auto()
a2 = auto()
check("auto increasing", a2 > a1)
check("auto >= 1", a1 >= 1)

# --- __future__ (fut) ---
from pure_lib.fut import _Feature, annotations

check("_Feature has compiler_flag", annotations.compiler_flag == 1048576)
check("_Feature has mandatory", annotations.mandatory == 0)

# --- collections (coll) ---
from pure_lib.coll import defaultdict, deque

dd = defaultdict(lambda: 0)
dd["a"] = 10
dd["b"] = 20
check("defaultdict set/get", dd["a"] == 10)
check("defaultdict default", dd["c"] == 0)
check("defaultdict contains", "a" in dd)

dq = deque()
dq.append(1)
dq.append(2)
dq.appendleft(0)
check("deque len", len(dq) == 3)
check("deque popleft", dq.popleft() == 0)
check("deque pop", dq.pop() == 2)
check("deque remaining", len(dq) == 1)

# --- unicodedata (udata) ---
from pure_lib.udata import lookup, normalize

check("lookup returns int", lookup("LATIN SMALL LETTER A") >= 0)
check("normalize returns", normalize("NFC", "hello") == "hello")

# --- Summary ---
print(f"\n{passed} passed, {failed} failed out of {passed + failed}")
if failed:
    sys.exit(1)
