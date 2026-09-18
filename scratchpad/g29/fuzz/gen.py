#!/usr/bin/env python3
"""G29 differential fuzzer: random small PyCSL programs, FALSE claim, look for a proof.

For each generated program we compute CPython's answer, then emit the SAME program with a
contract that is FALSE of it (`ensures \\result == v + 1`). PyCSL must NOT prove that.
Any `Verification SUCCESS` is a false proof (a candidate route).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
random.seed(SEED)
os.makedirs(OUT, exist_ok=True)

INT = lambda: str(random.randint(-4, 6))


def expr(depth, vars_):
    if depth <= 0 or random.random() < 0.3:
        return random.choice([INT(), random.choice(vars_) if vars_ else INT()])
    a, b = expr(depth - 1, vars_), expr(depth - 1, vars_)
    op = random.choice(["+", "-", "*", "//", "%", "&", "|", "^", ">>", "<<"])
    if op in ("//", "%"):
        return f"({a} {op} ({b} if {b} != 0 else 1))"
    if op in (">>", "<<"):
        return f"({a} {op} (abs({b}) % 4))"
    return f"({a} {op} {b})"


def stmts(depth, vars_, indent):
    out = []
    pad = "    " * indent
    k = random.randint(1, 3)
    for _ in range(k):
        r = random.random()
        if r < 0.35 or depth <= 0:
            v = f"v{len(vars_)}"
            out.append(f"{pad}{v} = {expr(2, vars_)}")
            vars_.append(v)
        elif r < 0.55:
            out.append(f"{pad}if {expr(1, vars_)} > {INT()}:")
            out += stmts(depth - 1, vars_, indent + 1)
            out.append(f"{pad}else:")
            out += stmts(depth - 1, vars_, indent + 1)
        elif r < 0.7 and vars_:
            tgt = random.choice(vars_)
            out.append(f"{pad}{tgt} = {expr(2, vars_)}")
        elif r < 0.85:
            out.append(f"{pad}xs = [{INT()}, {INT()}, {INT()}]")
            out.append(f"{pad}xs[{random.randint(0, 2)}] = {expr(1, vars_)}")
            v = f"v{len(vars_)}"
            out.append(f"{pad}{v} = xs[{random.randint(0, 2)}] + len(xs)")
            vars_.append(v)
        else:
            v = f"v{len(vars_)}"
            out.append(f"{pad}{v} = 0")
            vars_.append(v)
            out.append(f"{pad}for i{indent} in range({random.randint(0, 3)}):")
            out.append(f"{pad}    {v} = {v} + i{indent}")
    return out


def program(i):
    vars_: list = []
    body = stmts(2, vars_, 1)
    ret = expr(2, vars_) if vars_ else INT()
    body.append(f"    return {ret}")
    return "from typing import List\n_ = 0  # anchor\n\n\ndef probe() -> int:\n" + "\n".join(body) + "\n"


found = 0
for i in range(N):
    src = program(i)
    path_run = os.path.join(OUT, f"run_{SEED}_{i}.py")
    open(path_run, "w").write(src + '\n\nif __name__ == "__main__":\n    print(probe())\n')
    try:
        out = subprocess.run([sys.executable, path_run], capture_output=True, text=True, timeout=10)
    except Exception:
        continue
    if out.returncode != 0 or not out.stdout.strip().lstrip("-").isdigit():
        continue
    v = int(out.stdout.strip())
    # FALSE claim: \result == v + 1
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
print(f"FUZZ-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
