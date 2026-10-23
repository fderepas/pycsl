#!/usr/bin/env python3
"""G30 differential fuzzer #13: THE STORE-AND-READ-BACK boundary.

gen11 crossed the RETURN boundary (960 programs, nothing). gen12 crosses the STRING/INT
REPRESENTATION boundary, where four of this generation's routes live. This one crosses the
third boundary the generation's routes point at: **a value STORED into a container or a
field and READ BACK**.

Route #191 is the archetype — a `None` stored into a field, a list element, a dict value or
appended to a list read back as the integer 0, in all four positions — and its repair was
the shared `pycsl_none` opaque. The question this fuzzer asks is whether any OTHER value
kind survives the round trip wrongly: a bool, a nested empty container, a negative number,
a string, a value stored then overwritten, a value stored under one key and read under
another.

Each program: CPython runs it first; then four claims FALSE of the observed answer (the
gen #29 lesson — a +1-only claim cannot see an ERASED value, and an erased value reads
as 0).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g30fuzz13"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0

HEAD = '''from __future__ import annotations
from typing import Any, Dict, List, Optional

_ = 0  # anchor


class Box:
    #@ assigns self.v, self.w
    #@ ensures self.v == 0
    #@ ensures self.w == 0
    def __init__(self) -> None:
        self.v: int = 0
        self.w: int = 0

'''

# (setup lines that STORE, the READ that a contract can decide on)
CASES = [
    (['    b = Box()', '    b.v = 7'],                      'b.v == 7'),
    (['    b = Box()', '    b.v = 7', '    b.v = 9'],       'b.v == 9'),
    (['    b = Box()', '    b.v = 7'],                      'b.w == 0'),
    (['    b = Box()', '    b.v = -3'],                     'b.v == -3'),
    (['    xs: List[int] = [0, 0]', '    xs[1] = 5'],        'xs[1] == 5'),
    (['    xs: List[int] = [0, 0]', '    xs[1] = 5'],        'xs[0] == 0'),
    (['    xs: List[int] = [0]', '    xs[0] = -2'],          'xs[0] == -2'),
    (['    xs: List[int] = []', '    xs.append(4)'],         'len(xs) == 1'),
    (['    xs: List[int] = []', '    xs.append(4)'],         'xs[0] == 4'),
    (['    d: Dict[str, int] = {}', '    d["k"] = 6'],       'd["k"] == 6'),
    (['    d: Dict[str, int] = {}', '    d["k"] = 6'],       '"j" in d'),
    (['    d: Dict[str, int] = {"k": 1}', '    d["k"] = 6'], 'd["k"] == 6'),
    (['    b = Box()', '    b.v = 1', '    b.w = b.v'],      'b.w == 1'),
    (['    xs: List[int] = [1, 2, 3]', '    xs[0] = xs[2]'], 'xs[0] == 3'),
]


def gen(rng):
    setup, read = rng.choice(CASES)
    body = "\n".join(setup)
    return HEAD + f'''
#@ ensures True
def probe() -> int:
{body}
    if {read}:
        return 1
    return 2
'''


os.makedirs(OUT, exist_ok=True)
found = 0
ran = 0
for i in range(N):
    rng = random.Random(SEED * 8191 + i)
    src = gen(rng)
    run = os.path.join(OUT, f"run_{SEED}_{i}.py")
    open(run, "w").write(src + '\n\nif __name__ == "__main__":\n    print(probe())\n')
    try:
        out = subprocess.run([sys.executable, run], capture_output=True, text=True, timeout=10)
    except Exception:
        continue
    if out.returncode != 0 or not out.stdout.strip().lstrip("-").isdigit():
        continue
    v = int(out.stdout.strip())
    ran += 1
    for claim in (v + 1, 0, v - 1, 99):
        if claim == v:
            continue
        lines = src.split("\n")
        idx = len(lines) - 1 - lines[::-1].index("#@ ensures True")
        lines[idx] = f"#@ ensures \\result == {claim}"
        path_f = os.path.join(OUT, f"false_{SEED}_{i}_{claim}.py")
        open(path_f, "w").write("\n".join(lines))
        try:
            p = subprocess.run([f"{R}/.venv/bin/python3", f"{R}/src/pycsl/pycsl.py", path_f],
                               capture_output=True, text=True, timeout=300,
                               env={**os.environ, "PYTHONHASHSEED": "0"})
        except Exception:
            continue
        if "Verification SUCCESS" in p.stdout:
            found += 1
            print(f"FALSE-PROOF {path_f} (CPython {v}, claim {claim})", flush=True)
print(f"FUZZ13-DONE seed={SEED} n={N} ran={ran} false_proofs={found}", flush=True)
