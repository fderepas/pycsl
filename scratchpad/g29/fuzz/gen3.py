#!/usr/bin/env python3
"""G29 differential fuzzer #3: classes, methods, contracts, handlers — the shapes gen #29's
exception-model routes came from.

Each program defines a small class with a contracted method and a driver that calls it
(through `self`, a local receiver, a constructor call or a module-global instance), sometimes
inside a `try`. CPython is run; the driver then claims something FALSE of the observed
behaviour (a wrong return value, or `no_exception E` for an E that CPython raises).
"""
import os
import random
import subprocess
import sys

R = "/home/fabrice/git/pycsl"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/g29fuzz3"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 0
EXCS = ["ValueError", "KeyError", "IndexError", "ZeroDivisionError"]


def gen(rng):
    body = []
    guard = rng.random() < 0.4
    raises = rng.random() < 0.5
    meth = ["    def go(self, v: int) -> int:"]
    if guard:
        meth = ["    #@ requires v != 0", "    #@ ensures \\result == 1"] + meth
        meth.append("        return v // v")
    elif raises:
        exc = rng.choice(EXCS[:1] + ["KeyError"])
        meth.append(f"        if v < 0:")
        meth.append(f"            raise {exc}()")
        meth.append("        return v")
    else:
        kind = rng.randrange(3)
        if kind == 0:
            meth.append("        return self.d[\"zz\"]")
        elif kind == 1:
            meth.append("        return self.xs[5]")
        else:
            meth.append("        return 10 // v")
    cls = ["class C:", "    def __init__(self) -> None:",
           "        self.d: Dict[str, int] = {\"a\": 1}",
           "        self.xs: List[int] = [1]"] + meth
    arg = rng.choice(["-1", "0", "2"])
    recv = rng.choice(["local", "ctor", "global"])
    call = {"local": "c.go(%s)" % arg, "ctor": "C().go(%s)" % arg,
            "global": "_g.go(%s)" % arg}[recv]
    drv = ["def probe() -> int:"]
    if recv == "local":
        drv.append("    c = C()")
    catch = rng.random() < 0.5
    if catch:
        exc = rng.choice(EXCS)
        drv += ["    try:", f"        v = {call}", f"    except {exc}:",
                "        return 9", "    return v * 0"]
    else:
        drv += [f"    v = {call}", "    return v * 0"]
    head = "from typing import Dict, List\n_ = 0  # anchor\n\n\n"
    mid = "\n".join(cls) + "\n\n\n"
    if recv == "global":
        mid += "_g = C()\n\n\n"
    return head + mid + "\n".join(drv) + "\n"


os.makedirs(OUT, exist_ok=True)
found = 0
for i in range(N):
    rng = random.Random(SEED * 977 + i)
    src = gen(rng)
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
print(f"FUZZ3-DONE seed={SEED} n={N} false_proofs={found}", flush=True)
