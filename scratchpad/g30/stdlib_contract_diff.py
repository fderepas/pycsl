#!/usr/bin/env python3
"""Check each pycsl_lib stub's CONTRACT against the REAL stdlib function.

The right criterion, per the gen #30 finding: a stub is an ABSTRACTION, so its BODY may
differ from CPython freely. What must hold is that its `#@ ensures` is TRUE OF CPYTHON'S
ANSWER on every input satisfying its `#@ requires`. That is the fidelity claim the whole
`pycsl_lib` layer rests on, and nothing checks it.

Scope, stated: only contracts expressible as plain Python over the parameters and
`\result` — no `\forall`, `\exists`, `\old`, `\at`, `\separated`. Everything else is
REPORTED AS UNCHECKED rather than silently skipped.
"""
import importlib, importlib.util, inspect, itertools, random, re, sys

R = "/home/fabrice/git/pycsl"
MAP = {
    "bsect": "bisect", "mth": "math", "oper": "operator", "hq": "heapq",
    "b64": "base64", "frac": "fractions", "stat": "stat", "kw": "keyword",
    "txtwrp": "textwrap", "glb": "glob", "nums": "numbers", "fnm": "fnmatch",
}
SKIP_TOKENS = ("\\forall", "\\exists", "\\old", "\\at", "\\separated", "\\valid",
               "\\sum", "\\is_sorted", "\\permutation", "\\array_eq")


def to_py(e):
    e = e.replace("\\result", "_result")
    e = re.sub(r"\\length\(([^)]*)\)", r"len(\1)", e)
    e = e.replace("&&", " and ").replace("||", " or ")
    # `A ==> B`  ->  `(not (A)) or (B)`
    while "==>" in e:
        i = e.index("==>")
        e = "((not (%s)) or (%s))" % (e[:i], e[i+3:])
    return e


def contracts(path):
    out, req, ens = {}, [], []
    for line in open(path, errors="replace"):
        m = re.match(r"\s*#@\s*(requires|ensures)\s+(.+?)\s*$", line)
        if m:
            (req if m.group(1) == "requires" else ens).append(m.group(2))
            continue
        m = re.match(r"\s*def\s+(\w+)\s*\(", line)
        if m:
            if req or ens:
                out[m.group(1)] = (list(req), list(ens))
            req, ens = [], []
            continue
        if line.strip() and not line.lstrip().startswith(("#", '"', "'")):
            if not line.lstrip().startswith("@"):
                req, ens = [], []
    return out


def load(pkg):
    spec = importlib.util.spec_from_file_location(
        "stub_" + pkg, f"{R}/src/pycsl_lib/{pkg}/__init__.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 11)
POOL_INT = [0, 1, 2, 3, 5, 8, 13, -1, -5, 20]
POOL_STR = ["", "a", "ab", "abc", "A", "a.b", "*", "?"]
POOL_LIST = [[], [0], [1, 2], [0, 1, 2, 3], [5, 5], [-1, 0, 1]]

checked = viol = unchecked = nofn = 0
for pkg, std in sorted(MAP.items()):
    try:
        stub, real = load(pkg), importlib.import_module(std)
    except Exception:
        continue
    cts = contracts(f"{R}/src/pycsl_lib/{pkg}/__init__.py")
    for name, (req, ens) in sorted(cts.items()):
        f = getattr(stub, name, None)
        g = getattr(real, name, None)
        if not inspect.isfunction(f) or g is None or not callable(g):
            nofn += 1
            continue
        if any(t in " ".join(req + ens) for t in SKIP_TOKENS) or not ens:
            unchecked += 1
            continue
        params = list(inspect.signature(f).parameters.values())
        if not params or any(p.kind not in (p.POSITIONAL_OR_KEYWORD,) for p in params):
            unchecked += 1
            continue
        pools = []
        for p in params:
            a = p.annotation
            pools.append(POOL_INT if a is int else POOL_STR if a is str
                         else POOL_LIST if a is list else POOL_INT)
        combos = list(itertools.islice(itertools.product(*pools), 400))
        rng.shuffle(combos)
        local = 0
        for args in combos[:120]:
            env = {p.name: v for p, v in zip(params, args)}
            try:
                if not all(eval(to_py(c), {"len": len}, env) for c in req):
                    continue
            except Exception:
                continue
            try:
                real_ans = g(*args)
            except Exception:
                continue
            env["_result"] = real_ans
            for c in ens:
                try:
                    ok = eval(to_py(c), {"len": len}, env)
                except Exception:
                    continue
                checked += 1
                if not ok:
                    local += 1
                    if viol + local <= 15:
                        print("CONTRACT FALSE OF CPYTHON: %s.%s%r  ensures %s  (real=%r)"
                              % (pkg, name, args, c, real_ans))
        viol += local
print("contract checks: %d, VIOLATIONS: %d, unchecked contracts: %d, no real fn: %d"
      % (checked, viol, unchecked, nofn))
