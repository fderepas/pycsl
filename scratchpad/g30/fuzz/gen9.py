#!/usr/bin/env python3
"""G30 differential fuzzer #9: THE ARGUMENT-COERCION SURFACE.

The surface `bin/check-argument-coercion.py` was built for. Routes #192 and #193 were both
SUBSTITUTIONS in `_coerce_dotted_args`, and both needed the same trick to be decisive: the
CALLEE must carry a contract that is TRUE of its own body AND READS the property the
substitution changes (`start == None`, `len(xs)`, `"a" in d`). A callee with `ensures True`
hides the defect completely, which is why the surface went unprobed for so long.

So every program here gives the callee a reading contract, then calls it with an actual the
coercion path has to do something with: a bare int, `None`, an empty list, an empty dict, a
generator expression, a comprehension, a real list. CPython first, then four claims FALSE of
the observed answer (the gen #29 lesson: a +1-only claim cannot see an ERASED value, and an
erased value reads as 0).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g30fuzz9"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0

HEAD = """from typing import Dict, List, Optional


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string):
        self.py_type: int = py_type
        self.string: str = string


_ = 0  # anchor


#@ class invariant 0 <= self.i
#@ class invariant self.i < \\length(self.toks)
#@ class invariant \\length(self.toks) >= 1
@mutable_state
class P:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0
"""

# (callee source, the actual to pass, what CPython computes for the call)
CALLEES = [
    # reads `is None` — route #192's shape
    ("""
    #@ requires True
    #@ ensures start == None ==> \\result == 1
    #@ assigns \\nothing
    def tag(self, start: Optional[Tok]) -> int:
        if start is None:
            return 1
        return 2
""", "tag", ["0", "None", "self.toks[0]", "1 - 1"]),
    # reads the LENGTH — route #193's shape
    ("""
    #@ requires True
    #@ ensures \\result == \\length(xs)
    #@ assigns \\nothing
    def count(self, xs: List[int]) -> int:
        return len(xs)
""", "count", ["[]", "[1, 2, 3]", "sorted(x for x in [3, 1, 2])",
               "[x for x in [1, 2, 3]]", "list(reversed([1, 2]))"]),
    # reads MEMBERSHIP
    ("""
    #@ requires True
    #@ ensures ("a" in d) ==> \\result == 1
    #@ assigns \\nothing
    def pick(self, d: Dict[str, int]) -> int:
        if "a" in d:
            return 1
        return 2
""", "pick", ["{}", '{"a": 1}', '{"b": 2}']),
    # reads a STRING length
    ("""
    #@ requires True
    #@ ensures \\result == \\strlen(s)
    #@ assigns \\nothing
    def slen(self, s: str) -> int:
        return len(s)
""", "slen", ['""', '"abc"', '"a" + "bc"']),
]


def gen(rng):
    body, name, actuals = rng.choice(CALLEES)
    actual = rng.choice(actuals)
    drv = [
        "",
        "    #@ requires True",
        "    #@ ensures True",
        "    #@ assigns \\nothing",
        "    def probe(self) -> int:",
        f"        return self.{name}({actual})",
    ]
    return HEAD + body + "\n".join(drv) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
ran = 0
for i in range(N):
    rng = random.Random(SEED * 977 + i)
    src = gen(rng)
    run = os.path.join(OUT, f"run_{SEED}_{i}.py")
    open(run, "w").write(
        src + '\n\nif __name__ == "__main__":\n'
              '    print(P([Tok(1, "x"), Tok(2, "y")]).probe())\n')
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
        idx = lines.index("    #@ ensures True")
        lines[idx] = f"    #@ ensures \\result == {claim}"
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
print(f"FUZZ9-DONE seed={SEED} n={N} ran={ran} false_proofs={found}", flush=True)
