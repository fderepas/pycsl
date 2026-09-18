#!/usr/bin/env python3
"""G29 differential fuzzer #7: WHICH CALLEE DOES THIS CALL SITE GET?

Five of gen #29's routes (#166, #185, #186, #188, #189) are one question asked five
ways, so this grammar asks it at random: two or three classes carrying the SAME method
name with DIFFERENT contracts, reached through a receiver spelled as a local, a
`self.<field>`, a module global, a two-level field chain, a list element, or a name
bound on two branches — with an optional `#@ raises` / `#@ requires` on the callee.

Same differential contract as gen1-6: run CPython, then claim something FALSE of the
answer it produced, and report any `Verification SUCCESS`.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz7"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def klass(name, val, kind, rng):
    out = [f"class {name}:", "    def __init__(self) -> None:", f"        self.k = {val}", ""]
    if kind == "plain":
        out += [f"    #@ ensures \\result == {val}",
                "    def get(self) -> int:", f"        return {val}"]
    elif kind == "guarded":
        out += ["    #@ requires self.k != 0",
                "    #@ ensures \\result == 1",
                "    def get(self) -> int:", "        return self.k // self.k"]
    else:  # raising
        out += ["    #@ raises ValueError when v < 0",
                "    def get(self, v: int) -> int:",
                "        if v < 0:", "            raise ValueError()", "        return v"]
    return "\n".join(out) + "\n"


def gen(rng):
    kinds = ["plain", "plain", "guarded", "raising"]
    k1 = rng.choice(kinds)
    k2 = rng.choice(kinds)
    v1, v2 = rng.randint(0, 3), rng.randint(0, 3)
    head = "from typing import List\n_ = 0  # anchor\n\n\n"
    body = klass("Alpha", v1, k1, rng) + "\n\n" + klass("Beta", v2, k2, rng) + "\n\n"
    arg = "" if k2 != "raising" else str(rng.choice([-1, 1]))
    recv = rng.randrange(6)
    if recv == 0:            # plain local
        drv = ["def probe() -> int:", "    o = Beta()", f"    return o.get({arg}) + 0"]
    elif recv == 1:          # module global
        body += "_g = Beta()\n\n\n"
        drv = ["def probe() -> int:", f"    return _g.get({arg}) + 0"]
    elif recv == 2:          # self.<field>
        body += ("class Outer:\n    def __init__(self) -> None:\n"
                 "        self.inner = Beta()\n\n"
                 "    def run(self) -> int:\n"
                 f"        return self.inner.get({arg}) + 0\n\n\n")
        drv = ["def probe() -> int:", "    o = Outer()", "    return o.run()"]
    elif recv == 3:          # two-level field chain
        body += ("class Mid:\n    def __init__(self) -> None:\n"
                 "        self.leaf = Beta()\n\n\n"
                 "class Top:\n    def __init__(self) -> None:\n"
                 "        self.mid = Mid()\n\n"
                 "    def run(self) -> int:\n"
                 f"        return self.mid.leaf.get({arg}) + 0\n\n\n")
        drv = ["def probe() -> int:", "    t = Top()", "    return t.run()"]
    elif recv == 4:          # list element
        drv = ["def probe() -> int:", "    xs: List[Beta] = [Beta()]",
               f"    return xs[0].get({arg}) + 0"]
    else:                    # two branches, two classes
        drv = ["def probe(flag: int) -> int:",
               "    if flag > 0:", "        o = Alpha()", "    else:", "        o = Beta()",
               f"    return o.get({arg}) + 0"]
    return head + body + "\n".join(drv) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 1301 + i)
    src = gen(rng)
    run = os.path.join(OUT, f"run_{SEED}_{i}.py")
    call = "probe(1)" if "def probe(flag" in src else "probe()"
    open(run, "w").write(src + f'\n\nif __name__ == "__main__":\n    print({call})\n')
    try:
        out = subprocess.run([sys.executable, run], capture_output=True, text=True, timeout=10)
    except Exception:
        continue
    if out.returncode != 0 or not out.stdout.strip().lstrip("-").isdigit():
        continue
    v = int(out.stdout.strip())
    lines = src.split("\n")
    hdr = "def probe(flag: int) -> int:" if "def probe(flag" in src else "def probe() -> int:"
    idx = lines.index(hdr)
    lines.insert(idx, f"#@ ensures \\result == {v + 1}")
    path_f = os.path.join(OUT, f"false_{SEED}_{i}.py")
    open(path_f, "w").write("\n".join(lines))
    try:
        p = subprocess.run([f"{R}/.venv/bin/python3", f"{R}/src/pycsl/pycsl.py", path_f],
                           capture_output=True, text=True, timeout=300,
                           env={**os.environ, "PYTHONHASHSEED": "0"})
    except Exception:
        continue
    if "Verification SUCCESS" in p.stdout:
        found += 1
        print(f"FALSE-PROOF {path_f} (CPython {v}, claim {v + 1})", flush=True)
print(f"FUZZ7-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
