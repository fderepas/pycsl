#!/usr/bin/env python3
"""G29 differential fuzzer #5: aliasing, global mutation, augmented assignment,
negative floor-division/modulo, default/keyword arguments, chained comparisons,
while/else and break.

Same differential contract as gen1-4: run CPython first, then claim something FALSE
of the observed answer and report any `Verification SUCCESS`.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz5"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def gen(rng):
    shape = rng.randrange(9)
    a = rng.randint(-4, 4)
    b = rng.choice([-3, -2, -1, 1, 2, 3])
    head = "from typing import List, Dict\n_ = 0  # anchor\n"
    if shape == 0:  # list aliasing
        body = [
            "def probe() -> int:",
            f"    xs: List[int] = [{a}, {b}]",
            "    ys: List[int] = xs",
            f"    ys[0] = {a + 7}",
            "    return xs[0]",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 1:  # aliasing through a call
        body = [
            "def bump(zs: List[int]) -> int:",
            "    zs[0] = zs[0] + 1",
            "    return 0",
            "",
            "",
            "def probe() -> int:",
            f"    xs: List[int] = [{a}, {b}]",
            "    bump(xs)",
            "    return xs[0]",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 2:  # global mutation by a callee
        body = [
            f"_g: int = {a}",
            "",
            "",
            "def tick() -> int:",
            "    global _g",
            "    _g = _g + 1",
            "    return _g",
            "",
            "",
            "def probe() -> int:",
            "    tick()",
            "    tick()",
            "    return _g",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 3:  # negative floor division / modulo
        op = rng.choice(["//", "%"])
        body = [
            "def probe() -> int:",
            f"    x: int = {a}",
            f"    y: int = {b}",
            f"    return x {op} y",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 4:  # default arguments
        body = [
            f"def f(x: int, y: int = {b}) -> int:",
            "    return x * 10 + y",
            "",
            "",
            "def probe() -> int:",
            f"    return f({a})" if rng.randrange(2) else f"    return f({a}, {a})",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 5:  # keyword arguments out of order
        body = [
            "def f(x: int, y: int) -> int:",
            "    return x - y",
            "",
            "",
            "def probe() -> int:",
            f"    return f(y={a}, x={b})",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 6:  # augmented assignment on a field / subscript
        body = [
            "class C:",
            "    def __init__(self) -> None:",
            f"        self.n = {a}",
            f"        self.xs: List[int] = [{a}, {b}]",
            "",
            "",
            "def probe() -> int:",
            "    c = C()",
            f"    c.n += {b}",
            f"    c.xs[0] -= {b}",
            "    return c.n + c.xs[0]",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    if shape == 7:  # chained comparison
        c = rng.randint(-3, 3)
        body = [
            "def probe() -> int:",
            f"    x: int = {a}",
            f"    return 1 if {b} < x < {c} else 0",
        ]
        return head + "\n\n" + "\n".join(body) + "\n"
    # shape 8: while/else and break
    n = rng.randint(0, 4)
    lim = rng.randint(0, 4)
    body = [
        "def probe() -> int:",
        "    i: int = 0",
        "    r: int = 0",
        f"    while i < {n}:",
        f"        if i == {lim}:",
        "            break",
        "        r = r + i",
        "        i = i + 1",
        "    else:",
        "        r = r + 100",
        "    return r",
    ]
    return head + "\n\n" + "\n".join(body) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 911 + i)
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
print(f"FUZZ5-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
