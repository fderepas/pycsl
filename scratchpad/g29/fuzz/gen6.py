#!/usr/bin/env python3
"""G29 differential fuzzer #6: the contract MECHANISMS rather than the expression grammar.

Each program pairs an ordinary computation with one opt-in mechanism — `#@ no_inline`,
an `#@ act` case split, `#@ interface` opacity, a `#@ lemma`, a ghost variable, a class
invariant, a loop invariant, `#@ assert` / `#@ check` — and then claims something FALSE
of the answer CPython actually produced. Same contract as gen1-5: report any
`Verification SUCCESS`.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz6"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
HEAD = "from typing import List\n_ = 0  # anchor\n"


def gen(rng):
    a = rng.randint(-3, 4)
    b = rng.randint(1, 4)
    shape = rng.randrange(8)
    if shape == 0:  # no_inline on a module-global instance
        return HEAD + "\n\n" + "\n".join([
            "class Lib:",
            "    def __init__(self) -> None:",
            f"        self.x: int = {a}",
            "",
            f"    #@ ensures \\result == {a}",
            "    #@ assigns \\nothing",
            "    #@ no_inline",
            "    def get(self) -> int:",
            "        return self.x",
            "",
            "",
            "_lib = Lib()",
            "",
            "",
            "def probe() -> int:",
            f"    return _lib.get() + {b}",
        ]) + "\n"
    if shape == 1:  # act case split
        return HEAD + "\n\n" + "\n".join([
            "#@ act pos:",
            "#@     given x > 0",
            "#@     ensures \\result == x",
            "#@ act neg:",
            "#@     given x <= 0",
            "#@     ensures \\result == 0 - x",
            "def myabs(x: int) -> int:",
            "    if x > 0:",
            "        return x",
            "    return 0 - x",
            "",
            "",
            "def probe() -> int:",
            f"    return myabs({a}) + myabs({-b})",
        ]) + "\n"
    if shape == 2:  # interface opacity
        return HEAD + "\n\n" + "\n".join([
            f"#@ ensures \\result == {a} * 2",
            f"#@ interface ensures \\result >= {min(a * 2, 0)}",
            "def twice() -> int:",
            f"        return {a} * 2",
            "",
            "",
            "def probe() -> int:",
            f"    return twice() + {b}",
        ]).replace("        return", "    return") + "\n"
    if shape == 3:  # lemma + use
        return HEAD + "\n\n" + "\n".join([
            "#@ lemma",
            "#@ ensures n + 0 == n",
            "def plus_zero(n: int) -> None:",
            "    pass",
            "",
            "",
            "def probe() -> int:",
            f"    return {a} + {b}",
        ]) + "\n"
    if shape == 4:  # ghost variable
        return HEAD + "\n\n" + "\n".join([
            "def probe() -> int:",
            f"    v: int = {a}",
            f"    #@ ghost g = {b}",
            f"    #@ assert g == {b}",
            f"    return v * {b}",
        ]) + "\n"
    if shape == 5:  # class invariant
        return HEAD + "\n\n" + "\n".join([
            f"#@ class invariant self.x >= {min(a, 0)}",
            "class C:",
            "    def __init__(self) -> None:",
            f"        self.x: int = {abs(a)}",
            "",
            f"    #@ ensures \\result == {abs(a)}",
            "    def get(self) -> int:",
            "        return self.x",
            "",
            "",
            "def probe() -> int:",
            "    c = C()",
            f"    return c.get() - {b}",
        ]) + "\n"
    if shape == 6:  # loop invariant + variant
        n = rng.randint(0, 4)
        return HEAD + "\n\n" + "\n".join([
            "def probe() -> int:",
            "    i: int = 0",
            "    s: int = 0",
            "    #@ loop invariant s == i",
            f"    #@ loop variant {n} - i",
            f"    while i < {n}:",
            "        s = s + 1",
            "        i = i + 1",
            f"    return s * {b}",
        ]) + "\n"
    # shape 7: assert / check checkpoints
    return HEAD + "\n\n" + "\n".join([
        "def probe() -> int:",
        f"    v: int = {a}",
        f"    #@ check v == {a}",
        f"    v = v + {b}",
        f"    #@ assert v == {a + b}",
        "    return v",
    ]) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 1129 + i)
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
    lines = src.split("\n")
    idx = lines.index("def probe() -> int:")
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
print(f"FUZZ6-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
