#!/usr/bin/env python3
"""G29 differential fuzzer #2: dict/list reads, None, handlers — the areas gen #29's routes came from.

Same contract: run CPython, then claim something FALSE of the observed answer and require PyCSL
NOT to prove it. Programs that raise in CPython are re-used with a `no_exception` claim instead
(`#@ no_exception <E>` on a program that raises E is a false claim).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz2"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 25
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
random.seed(SEED)
os.makedirs(OUT, exist_ok=True)

KEYS = ['"a"', '"b"', '"c"']
EXCS = ["KeyError", "IndexError", "ZeroDivisionError", "ValueError"]


def body(rng):
    lines = []
    lines.append('    d: Dict[str, int] = {"a": 1}')
    lines.append("    xs: List[int] = [1, 2]")
    lines.append("    v = 0")
    kind = rng.randrange(6)
    if kind == 0:
        lines.append(f"    v = d[{rng.choice(KEYS)}]")
    elif kind == 1:
        lines.append(f"    v = xs[{rng.randrange(4)}]")
    elif kind == 2:
        lines.append(f"    v = 10 // ({rng.randrange(3)})" if rng.random() < 0.5 else "    v = 10 // (len(xs) - 2)")
    elif kind == 3:
        lines.append('    v = int("%s")' % rng.choice(["1", "x", "2.5"]))
    elif kind == 4:
        lines.append("    ys: List[int] = []")
        lines.append("    v = ys[0]" if rng.random() < 0.5 else "    ys.append(1)\n    v = ys[0]")
    else:
        lines.append("    o: Optional[int] = None")
        lines.append("    v = 1 if o == 0 else 2")
    if rng.random() < 0.5:
        exc = rng.choice(EXCS)
        lines = ["    try:"] + ["    " + ln for ln in lines] + [
            f"    except {exc}:", "        return 9"]
        lines = ['    d: Dict[str, int] = {"a": 1}', "    xs: List[int] = [1, 2]"] + lines
    lines.append("    return v")
    return lines


head = "from typing import Dict, List, Optional\n_ = 0  # anchor\n\n\n"
found = 0
for i in range(N):
    rng = random.Random(SEED * 1000 + i)
    src = head + "def probe() -> int:\n" + "\n".join(body(rng)) + "\n"
    run = os.path.join(OUT, f"run_{SEED}_{i}.py")
    open(run, "w").write(src + '\n\nif __name__ == "__main__":\n    print(probe())\n')
    try:
        out = subprocess.run([sys.executable, run], capture_output=True, text=True, timeout=10)
    except Exception:
        continue
    lines = src.split("\n")
    idx = lines.index("def probe() -> int:")
    if out.returncode == 0 and out.stdout.strip().lstrip("-").isdigit():
        v = int(out.stdout.strip())
        lines.insert(idx, f"#@ ensures \\result == {v + 1}")
        why = f"CPython {v}, claim {v + 1}"
    else:
        exc = out.stderr.strip().split("\n")[-1].split(":")[0].strip()
        if exc not in EXCS:
            continue
        lines.insert(idx, f"#@ no_exception {exc}")
        lines.insert(idx, "#@ ensures \\result == 0")
        why = f"CPython raises {exc}, claim no_exception {exc}"
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
        print(f"FALSE-PROOF {path_f} ({why})", flush=True)
print(f"FUZZ2-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
