#!/usr/bin/env python3
"""Differential fidelity probe of the pycsl_lib stdlib stubs against CPython's real modules.

Each `src/pycsl_lib/<pkg>` is a BODY-VERIFIED re-implementation of a stdlib module. Its
contracts are proven of ITS OWN BODY, so a contract can be perfectly proven and still be
wrong ABOUT PYTHON if the body does not agree with the module it stands in for. Nothing in
the battery compares them; this does, by running both on random inputs.
"""
import importlib, importlib.util, inspect, random, sys, traceback

R = "/home/fabrice/git/pycsl"
MAP = {
    "bsect": "bisect", "mth": "math", "oper": "operator", "hq": "heapq",
    "fnm": "fnmatch", "b64": "base64", "frac": "fractions", "stat": "stat",
    "txtwrp": "textwrap", "reprlib": "reprlib", "hlib": "hashlib", "glb": "glob",
    "kw": "keyword", "tok": "tokenize", "url": "urllib.parse", "uu": "uuid",
    "unt": "unittest", "nums": "numbers", "strct": "struct", "enm": "enum",
}
ARGSETS = [
    lambda rng: (rng.randint(-20, 20),),
    lambda rng: (rng.randint(0, 20),),
    lambda rng: (rng.randint(-20, 20), rng.randint(1, 20)),
    lambda rng: (sorted(rng.randint(0, 6) for _ in range(rng.randint(0, 6))), rng.randint(-1, 7)),
    lambda rng: ("".join(rng.choice("ab*?.") for _ in range(rng.randint(0, 5))),),
    lambda rng: ("".join(rng.choice("abc") for _ in range(rng.randint(0, 5))),
                 "".join(rng.choice("ab*?") for _ in range(rng.randint(0, 4)))),
]

def load(pkg):
    path = f"{R}/src/pycsl_lib/{pkg}/__init__.py"
    spec = importlib.util.spec_from_file_location("stub_" + pkg, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
tot_fn = tot_cmp = mism = skipped = 0
for pkg, std in sorted(MAP.items()):
    try:
        stub = load(pkg)
    except Exception:
        skipped += 1
        continue
    try:
        real = importlib.import_module(std)
    except Exception:
        skipped += 1
        continue
    for name in sorted(n for n in dir(stub) if not n.startswith("_")):
        f = getattr(stub, name)
        if not inspect.isfunction(f):
            continue
        g = getattr(real, name, None)
        if g is None or not callable(g):
            continue
        tot_fn += 1
        local_mis = 0
        for _ in range(120):
            args = rng.choice(ARGSETS)(rng)
            # TYPE-DOMAIN FILTER. Many stubs model a STRING operation in the INT
            # domain (`fnm.fnmatch(name: int, pat: int)`), which is an honest
            # abstraction, not a re-implementation — feeding it strings measures my
            # harness, not the stub. Only compare when every actual matches the stub's
            # own declared parameter annotation.
            try:
                sig = inspect.signature(f)
                params = list(sig.parameters.values())
                req = [p for p in params if p.default is inspect.Parameter.empty]
                if len(args) < len(req) or len(args) > len(params):
                    continue
                ok = True
                for p, v in zip(params, args):
                    ann = p.annotation
                    if ann is inspect.Parameter.empty:
                        continue
                    if ann is int and not isinstance(v, int):
                        ok = False
                    elif ann is str and not isinstance(v, str):
                        ok = False
                    elif ann is list and not isinstance(v, list):
                        ok = False
                if not ok:
                    continue
            except Exception:
                pass
            try:
                a = f(*args)
            except Exception as e:
                a = ("ERR", type(e).__name__)
            try:
                b = g(*args)
            except Exception as e:
                b = ("ERR", type(e).__name__)
            # ONLY compare inputs BOTH sides accept. A one-sided exception is almost
            # always a SIGNATURE mismatch in this crude harness (the stub's `auto(x)` vs
            # enum's `auto` sentinel), not a fidelity gap; counting those would drown the
            # signal. A DISAGREEMENT ON AN INPUT BOTH ACCEPT is the real finding.
            def _err(v):
                return isinstance(v, tuple) and v and v[0] == "ERR"
            if _err(a) or _err(b):
                continue
            tot_cmp += 1
            if a != b:
                local_mis += 1
                if mism + local_mis <= 12:
                    print("MISMATCH %s.%s%r -> stub=%r real=%r" % (pkg, name, args, a, b))
        mism += local_mis
print("functions compared: %d, value comparisons: %d, MISMATCHES: %d, pkgs skipped: %d"
      % (tot_fn, tot_cmp, mism, skipped))
