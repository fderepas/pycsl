#!/usr/bin/env python3
"""G30 differential fuzzer #11: THE RETURN BOUNDARY, read by the caller.

gen9/gen10 crossed the ARGUMENT boundary — a callee whose contract READS the property the
emitter substitutes. Four of gen #30's seven routes came out of that shape. This is its
mirror image: the CALLEE returns a value whose representation the emitter may stand in for,
and the CALLER's contract READS a property of what came back.

Why it is worth crossing separately: at the argument boundary the substitution happens at
the CALL SITE (`_coerce_dotted_args`), and at the return boundary it happens inside the
callee's own lowering and then has to survive the callee's declared return type. The two
code paths are disjoint, and the argument one is now gated by
`bin/check-argument-coercion.py` while the return one is not gated by anything — the
argument-coercion plane says so itself ("the RETURN side ... is the mirror image of this and
has no plane yet — the honest gap in this instrument").

Each program: CPython runs it first; then four claims FALSE of the observed answer
(the gen #29 lesson — a +1-only claim cannot see an ERASED value, and an erased value
reads as 0).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g30fuzz11"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 16
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0

HEAD = '''from __future__ import annotations
from typing import Any, Dict, List, Optional

_ = 0  # anchor


class Tok:
    def __init__(self, py_type, string):
        self.py_type: int = py_type
        self.string: str = string

'''

# (callee decl, callee body, the caller expression reading the result)
CALLEES = [
    ("def mk() -> List[int]:", "    return []", "len(mk())"),
    ("def mk() -> List[int]:", "    return [1, 2, 3]", "len(mk())"),
    ("def mk() -> List[int]:", "    return sorted(x for x in [3, 1, 2])", "len(mk())"),
    ("def mk() -> List[int]:", "    return [x for x in [1, 2]]", "len(mk())"),
    ("def mk() -> List[int]:", "    return list(reversed([1, 2]))", "len(mk())"),
    ("def mk() -> str:", '    return ""', "len(mk())"),
    ("def mk() -> str:", '    return "abc"', "len(mk())"),
    ("def mk() -> str:", '    return "a" + "bc"', "len(mk())"),
    ("def mk() -> Optional[int]:", "    return None", "1 if mk() == 0 else 2"),
    ("def mk() -> Optional[int]:", "    return 5", "1 if mk() == 0 else 2"),
    ("def mk() -> Dict[str, int]:", "    return {}", '1 if "a" in mk() else 2'),
    ("def mk() -> Dict[str, int]:", '    return {"a": 1}', '1 if "a" in mk() else 2'),
    ("def mk() -> int:", "    return getattr(_anyobj(), \"a\", 0)", "1 if mk() == 0 else 2"),
]

EXTRA = '''

class _C:
    def __init__(self):
        self.a: int = 7


def _anyobj() -> Any:
    return _C()
'''


def gen(rng):
    decl, body, read = rng.choice(CALLEES)
    needs_any = "_anyobj" in body
    src = HEAD + (EXTRA if needs_any else "") + f'''

#@ requires True
#@ ensures True
{decl}
{body}


#@ ensures True
def probe() -> int:
    return {read}
'''
    return src


os.makedirs(OUT, exist_ok=True)
found = 0
ran = 0
for i in range(N):
    rng = random.Random(SEED * 6301 + i)
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
        # the LAST `#@ ensures True` is the caller's
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
print(f"FUZZ11-DONE seed={SEED} n={N} ran={ran} false_proofs={found}", flush=True)
