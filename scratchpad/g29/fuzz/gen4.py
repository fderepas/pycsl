#!/usr/bin/env python3
"""G29 differential fuzzer #4: contracts over fields, inheritance, global instances, folds.

Deeper grammar than gen3: a base/derived pair with contracted methods, a module-global
instance (inlined by the frontend), `any`/`all`/`sum` folds and slices. Same differential
contract: CPython first, then a claim FALSE of the observed answer.
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz4"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0


def gen(rng):
    base_ret = rng.choice(["self.n", "self.n + 1", "len(self.xs)", "self.xs[0]"])
    sub_ret = rng.choice(["self.n * 2", "0 - self.n", "len(self.xs) + 1", "self.xs[0] - 1"])
    ens = rng.choice(["#@ ensures \\result >= 0", "#@ ensures \\result == self.n", ""])
    cls = [
        "class A:",
        "    def __init__(self) -> None:",
        "        self.n = %d" % rng.randint(0, 3),
        "        self.xs: List[int] = [%d, %d]" % (rng.randint(0, 3), rng.randint(0, 3)),
    ]
    if ens:
        cls.append("    " + ens)
    cls += ["    def val(self) -> int:", f"        return {base_ret}",
            "",
            "    def twice(self) -> int:",
            "        return self.val() * 2",
            "",
            "",
            "class B(A):",
            "    def val(self) -> int:", f"        return {sub_ret}"]
    use = rng.randrange(5)
    drv = ["def probe() -> int:"]
    if use == 0:
        drv += ["    b = B()", "    return b.twice()"]
    elif use == 1:
        drv += ["    a = A()", "    return a.twice() + _g.val()"]
    elif use == 2:
        drv += ["    xs: List[int] = [1, 2, 3]",
                "    return sum(xs[0:%d])" % rng.randint(0, 3)]
    elif use == 3:
        drv += ["    xs: List[int] = [%d, %d]" % (rng.randint(0, 2), rng.randint(0, 2)),
                "    return 1 if any(x > 1 for x in xs) else 0"]
    else:
        drv += ["    xs: List[int] = [%d, %d]" % (rng.randint(0, 2), rng.randint(0, 2)),
                "    return 1 if all(x >= 1 for x in xs) else 0"]
    head = "from typing import List\n_ = 0  # anchor\n\n\n"
    return head + "\n".join(cls) + "\n\n\n_g = A()\n\n\n" + "\n".join(drv) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 613 + i)
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
print(f"FUZZ4-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
