#!/usr/bin/env python3
"""G29 differential fuzzer #8: SLICES and STRING operations.

Route #190 lived here — an omitted slice bound lowered to the integer 0 and Why3's
`String.substring` answered the empty string for the negative length that produced. This
grammar walks the neighbourhood: every combination of present/omitted/negative slice
bounds on a `str` and on a `List[int]`, and the string builtins whose bridges carry a
length or content law (`find`, `replace`, `upper`, `strip`, `*`, `+`, `in`).

Same differential contract as gen1-7: run CPython, then claim something FALSE of the
answer it produced, and report any `Verification SUCCESS`.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz8"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
HEAD = "from typing import List\n_ = 0  # anchor\n\n\n"


def bound(rng):
    r = rng.randrange(4)
    if r == 0:
        return ""
    if r == 1:
        return str(rng.randint(0, 4))
    if r == 2:
        return "0 - %d" % rng.randint(1, 4)
    return "n"


def gen(rng):
    shape = rng.randrange(6)
    lo, hi = bound(rng), bound(rng)
    if shape == 0:  # string slice, length claimed
        return HEAD + "\n".join([
            "def probe() -> int:",
            "    n: int = 2",
            '    s: str = "abcde"',
            f"    t: str = s[{lo}:{hi}]",
            "    return len(t)",
        ]) + "\n"
    if shape == 1:  # string slice, content compared
        return HEAD + "\n".join([
            "def probe() -> int:",
            "    n: int = 2",
            '    s: str = "abcde"',
            f"    t: str = s[{lo}:{hi}]",
            '    if t == "bc":',
            "        return 1",
            "    return 0",
        ]) + "\n"
    if shape == 2:  # list slice, length claimed
        return HEAD + "\n".join([
            "def probe() -> int:",
            "    n: int = 2",
            "    xs: List[int] = [1, 2, 3, 4, 5]",
            f"    ys: List[int] = xs[{lo}:{hi}]",
            "    return len(ys)",
        ]) + "\n"
    if shape == 3:  # find / index arithmetic
        pat = rng.choice(['"a"', '"e"', '"z"', '"cd"'])
        return HEAD + "\n".join([
            "def probe() -> int:",
            '    s: str = "abcde"',
            f"    return s.find({pat}) + 1",
        ]) + "\n"
    if shape == 4:  # repeat / concat lengths
        k = rng.randint(-2, 3)
        return HEAD + "\n".join([
            "def probe() -> int:",
            '    s: str = "ab"',
            f"    t: str = s * {k} if {k} >= 0 else s",
            '    u: str = t + "xyz"',
            "    return len(u)",
        ]) + "\n"
    # shape 5: upper / strip / membership
    op = rng.choice(["s.upper()", "s.strip()", "s.lower()"])
    return HEAD + "\n".join([
        "def probe() -> int:",
        '    s: str = " aB "',
        f"    t: str = {op}",
        "    return len(t)",
    ]) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 1487 + i)
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
    # MORE THAN ONE FALSE CLAIM PER PROGRAM. A fuzzer that only ever claims `answer + 1`
    # catches a model that answers `answer + 1` and NOTHING ELSE — measured: route #190
    # makes `len("abcde"[1:])` answer 0 where CPython answers 4, and this grammar walked
    # straight past it for a whole batch because it only asked about 5. So ask about a
    # SET of wrong answers, including the degenerate 0 that an erased value produces.
    for claim in (v + 1, 0, v - 1, 99):
        if claim == v:
            continue
        lines = src.split("\n")
        idx = lines.index("def probe() -> int:")
        lines.insert(idx, f"#@ ensures \\result == {claim}")
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
print(f"FUZZ8-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
