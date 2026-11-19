#!/usr/bin/env python3
"""G30 differential fuzzer #10: THE READING-CALLEE cross-product.

Four of gen #30's six routes (#192, #194, #195, #196) came from ONE probe shape, and the
shape is the whole point:

    the CALLEE carries a contract that is TRUE of its own body and that READS a property
    of the argument; the CALL SITE passes an actual whose REPRESENTATION the emitter
    substitutes, erases, or stands in for.

A callee with `ensures True` hides every defect of that family completely, which is why the
surface survived 190 routes. gen9 probed four hand-picked callees; this crosses them
systematically: seven parameter shapes x five reading contracts x eleven actuals, filtered
to the combinations that are well-typed enough for CPython to produce an integer, then four
claims FALSE of that integer (the gen #29 lesson: a +1-only claim cannot see an ERASED
value, and an erased value reads as 0).

Runs indefinitely over seeds; every FALSE-PROOF line is a route candidate with its file.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g30fuzz10"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0

HEAD = '''from __future__ import annotations
from typing import Dict, List, Optional


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
'''

# (param decl, reading `ensures`, body, list of actuals that CPython accepts)
CALLEES = [
    ("p", "p == 0 ==> \\result == 1",
     "        if p == 0:\n            return 1\n        return 2",
     ["[]", "{}", "0", "sorted(x for x in [3, 1, 2])", "[1, 2, 3]",
      "[x for x in [1, 2]]", '""', "self.toks[0]"]),
    ("ns: List[int]", "\\result == \\length(ns)",
     "        return len(ns)",
     ["[]", "[1, 2, 3]", "sorted(x for x in [3, 1, 2])", "[x for x in [1, 2]]",
      "list(reversed([1, 2]))"]),
    ("d: Dict[str, int]", '("a" in d) ==> \\result == 1',
     '        if "a" in d:\n            return 1\n        return 2',
     ["{}", '{"a": 1}', '{"b": 2}', '{"a": 0, "b": 1}']),
    ("s: str", "\\result == \\strlen(s)",
     "        return len(s)",
     ['""', '"abc"', '"a" + "bc"', '"x" * 2']),
    ("t: Optional[Tok]", "t == None ==> \\result == 1",
     "        if t is None:\n            return 1\n        return 2",
     ["None", "self.toks[0]", "0"]),
    ("v: Optional[str] = None", "v == None ==> \\result == 1",
     "        if v is None:\n            return 1\n        return 2",
     ["None", '"z"', "0", ""]),
]


def gen(rng):
    decl, ens, body, actuals = rng.choice(CALLEES)
    actual = rng.choice(actuals)
    name = "cal"
    call = f"self.{name}()" if actual == "" else f"self.{name}({actual})"
    src = HEAD + f'''
    #@ requires True
    #@ ensures {ens}
    #@ assigns \\nothing
    def {name}(self, {decl}) -> int:
{body}

    #@ requires True
    #@ ensures True
    #@ assigns \\nothing
    def probe(self) -> int:
        return {call}
'''
    return src


os.makedirs(OUT, exist_ok=True)
found = 0
ran = 0
for i in range(N):
    rng = random.Random(SEED * 7919 + i)
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
print(f"FUZZ10-DONE seed={SEED} n={N} ran={ran} false_proofs={found}", flush=True)
