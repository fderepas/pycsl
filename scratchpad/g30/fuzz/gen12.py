#!/usr/bin/env python3
"""G30 differential fuzzer #12: THE STRING/INT REPRESENTATION BOUNDARY.

FOUR of this generation's routes live here and nowhere else:

  #199  the EMPTY f-string was the integer 0
  #200  a string literal actual was HASHED into a declared int parameter
  #202  the same hash through an un-annotated parameter and the keyword slot
  #203  a SINGLE-PART f-string WAS the integer it interpolates

The shared mechanism is that PyCSL carries strings in two models — a real Why3 `string`
and an int-hash domain — and a value that crosses between them can come back as a number
a comparison DECIDES against. gen9/gen10 crossed the argument boundary and gen11 the
return boundary; this one crosses the REPRESENTATION boundary, which is orthogonal to
both: it builds a string by every route the emitter has, reads it with a comparison or a
length, and checks whether the model decides something CPython does not.

Each program: CPython runs it first, then four claims FALSE of the observed answer
(the gen #29 lesson — a +1-only claim cannot see an ERASED value, and an erased value
reads as 0).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g30fuzz12"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0

HEAD = '''from __future__ import annotations
from typing import Any, Dict, List, Optional

_ = 0  # anchor

'''

# (setup lines that BUILD a string, the READ that a contract can decide on)
BUILDERS = [
    (['    n = 5', '    s = f"{n}"'],            's == "5"'),
    (['    n = 5', '    s = f"x{n}"'],           's == "x5"'),
    (['    n = 5', '    s = f"{n}y"'],           's == "5y"'),
    (['    n = 5', '    s = f"{n}{n}"'],         's == "55"'),
    (['    s = f""'],                            's == ""'),
    (['    n = 5', '    s = str(n)'],            's == "5"'),
    (['    n = 5', '    s = "%d" % n'],          's == "5"'),
    (['    s = "ab" + "cd"'],                    's == "abcd"'),
    (['    a = "ab"', '    b = "cd"', '    s = a + b'], 's == "abcd"'),
    (['    s = "ab" * 2'],                       's == "abab"'),
    (['    s = ",".join(["a", "b"])'],           's == "a,b"'),
    (['    s = "AB".lower()'],                   's == "ab"'),
    (['    s = "ab".upper()'],                   's == "AB"'),
    (['    s = "abc"[1:]'],                      's == "bc"'),
    (['    s = "abc".replace("b", "z")'],        's == "azc"'),
    (['    s = "  ab  ".strip()'],               's == "ab"'),
    (['    n = 5', '    s = f"{n}"'],            'len(s) == 1'),
    (['    s = "ab" + "cd"'],                    'len(s) == 4'),
    (['    s = f""'],                            'len(s) == 0'),
    (['    n = 5', '    s = f"{n}"'],            's != "6"'),
]


def gen(rng):
    setup, read = rng.choice(BUILDERS)
    body = "\n".join(setup)
    src = HEAD + f'''
#@ ensures True
def probe() -> int:
{body}
    if {read}:
        return 1
    return 2
'''
    return src


os.makedirs(OUT, exist_ok=True)
found = 0
ran = 0
for i in range(N):
    rng = random.Random(SEED * 7919 + i)
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
print(f"FUZZ12-DONE seed={SEED} n={N} ran={ran} false_proofs={found}", flush=True)
