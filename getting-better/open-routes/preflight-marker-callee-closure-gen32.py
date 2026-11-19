#!/usr/bin/env python3
r"""TRIAGE every `#@ \trusted` marker by its live body's CALLEE CLOSURE, not by its line count.

WHY (wall-lesson (o4)). Gen #32 picked two conversion candidates by the size of their live body and
both were refuted in minutes by their callees — `_expr_to_whyml_string_ctx` (24 lines) by a
three-word call, and all four of `abstract_ops.py`'s stubs by regex/`.setdefault`/`.join`/`.items`.
Size is a proxy and it pointed at the wrong candidates. The closure is the cost.

THREE VERDICTS, in increasing order of usefulness:

  BLOCKED   the live body uses a construct this campaign has MEASURED as unlowerable — the in-place
            mutators behind one refusal, `.setdefault`, `str.join`, dict `.items()`/`.values()`
            iteration, or `re`.
  NET-ZERO  the body calls a FREE function the mirror tree does not define and the call is not
            int-shaped, OR a `self.<m>()` the DESTINATION FILE does not define (which
            auto-synthesizes a RECEIVER-LESS `val` with an unconstrained result). Per wall-lesson (r4): an unresolved free call auto-synthesizes
            `val <name> (x0: int) : int`, so a string/array/record-shaped callee needs a TYPED
            redeclaration in the mirror — and a typed redeclaration IS a `\trusted` marker. Removing
            one marker and adding one is NET ZERO on the count, whatever it buys in proof strength.
  CLEAR     neither of the above. NECESSARY, NEVER SUFFICIENT — the biggest wall in this repo is the
            int-erasure SEAM, which is type-shaped and invisible to a call-shaped filter, so ALWAYS
            join the output against `getting-better/trusted-reasons.tsv` (`--join`), which already
            classifies it for 102 markers.

Usage:  getting-better/open-routes/preflight-marker-callee-closure-gen32.py [--join] [--list-clear]
"""
import argparse
import ast
import builtins
import collections
import os
import sys

MIRROR, LIVE = "src/self-annotate/src", "src/pycsl"
BLOCKED_METHODS = {
    "pop": "in-place-mutator", "extend": "in-place-mutator", "update": "in-place-mutator",
    "insert": "in-place-mutator", "sort": "in-place-mutator", "remove": "in-place-mutator",
    "reverse": "in-place-mutator", "setdefault": "setdefault-refusal",
    "join": "str.join", "items": "dict-items-iteration", "values": "dict-values-iteration",
    "findall": "regex", "match": "regex", "sub": "regex", "search": "regex", "compile": "regex",
}
INT_SHAPED = {"int", "bool", "None", None}


def marked(path):
    """the qualnameless names of defs carrying a `#@ \trusted` marker in their preceding block."""
    lines = open(path, encoding="utf-8").read().splitlines()
    out = []
    for n in ast.walk(ast.parse("\n".join(lines))):
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        i = n.lineno - 2
        while i >= 0:
            s = lines[i].strip()
            if not (s.startswith("#") or s.startswith("@") or not s):
                break
            if s.startswith(r"#@ \trusted"):
                out.append(n.name); break
            i -= 1
    return out


def bound_inside(node):
    """Every name the body itself binds. The four classes a naive scan misses (lesson (q4)):
    parameters incl. `cls`, nested `def`/`lambda`, tuple/for/with/except targets, and function-LOCAL
    imports."""
    b = set()
    a = node.args
    for p in list(a.args) + list(a.kwonlyargs) + list(getattr(a, "posonlyargs", [])):
        b.add(p.arg)
    if a.vararg: b.add(a.vararg.arg)
    if a.kwarg: b.add(a.kwarg.arg)
    for x in ast.walk(node):
        if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and x is not node:
            b.add(x.name)
        if isinstance(x, ast.Lambda):
            for p in list(x.args.args) + list(x.args.kwonlyargs): b.add(p.arg)
        if isinstance(x, (ast.Import, ast.ImportFrom)):          # function-LOCAL import
            for al in x.names: b.add(al.asname or al.name.split(".")[0])
        tgts = ([x.target] if isinstance(x, (ast.For, ast.AsyncFor, ast.comprehension,
                                             ast.AnnAssign, ast.NamedExpr)) else
                x.targets if isinstance(x, ast.Assign) else [])
        for t in tgts:
            if t is None: continue
            for nn in ast.walk(t):
                if isinstance(nn, ast.Name): b.add(nn.id)
        if isinstance(x, ast.withitem) and x.optional_vars is not None:
            for nn in ast.walk(x.optional_vars):
                if isinstance(nn, ast.Name): b.add(nn.id)
        if isinstance(x, ast.ExceptHandler) and x.name: b.add(x.name)
    return b


def ann(node):
    return node.id if isinstance(node, ast.Name) else (
        ast.unparse(node) if node is not None else None)


def int_shaped(fn_node):
    """(r4) is the free callee's signature int-shaped, so the `int -> int` auto-synthesis is free?"""
    for p in list(fn_node.args.args) + list(fn_node.args.kwonlyargs):
        if p.arg in ("self", "cls"): continue
        if ann(p.annotation) not in INT_SHAPED: return False
    return ann(fn_node.returns) in INT_SHAPED


def index(root):
    defs, modlevel = collections.defaultdict(list), set()
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for fn in sorted(fns):
            if not fn.endswith(".py"): continue
            p = os.path.join(dp, fn)
            try: t = ast.parse(open(p, encoding="utf-8").read())
            except Exception: continue
            for n in ast.walk(t):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defs[n.name].append((p, n))
            for st in t.body:
                if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    modlevel.add(st.name)
                elif isinstance(st, ast.Assign):
                    for tg in st.targets:
                        if isinstance(tg, ast.Name): modlevel.add(tg.id)
                elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    modlevel.add(st.target.id)
                elif isinstance(st, ast.ImportFrom):
                    for al in st.names: modlevel.add(al.asname or al.name)
                elif isinstance(st, ast.Import):
                    for al in st.names: modlevel.add((al.asname or al.name).split(".")[0])
    return defs, modlevel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--join", action="store_true", help="join against trusted-reasons.tsv")
    ap.add_argument("--list-clear", action="store_true")
    args = ap.parse_args()

    live_defs, _ = index(LIVE)
    _, mirror_modlevel = index(MIRROR)
    mirror_methods = {}
    for dp, dn, fns in os.walk(MIRROR):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for fn in sorted(fns):
            if not fn.endswith(".py"): continue
            mp = os.path.join(dp, fn)
            try: t = ast.parse(open(mp, encoding="utf-8").read())
            except Exception: continue
            mirror_methods[mp.replace(MIRROR + "/", "")] = {
                n.name for n in ast.walk(t)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    reasons = {}
    for ln in open("getting-better/trusted-reasons.tsv"):
        if ln.startswith("#") or ln.startswith("file\t"): continue
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3: reasons[(f[0], f[1])] = f[2]

    rows = []
    for dp, dn, fns in os.walk(MIRROR):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for fn in sorted(fns):
            if not fn.endswith(".py"): continue
            mp = os.path.join(dp, fn); lp = mp.replace(MIRROR, LIVE, 1)
            rel = mp.replace(MIRROR + "/", "")
            for name in marked(mp):
                cands = live_defs.get(name, [])
                pick = next((c for c in cands if c[0] == lp), cands[0] if cands else None)
                if pick is None:
                    rows.append((rel, name, "NO-LIVE-DEF", [], 0)); continue
                _, node = pick
                blk = sorted({BLOCKED_METHODS[x.func.attr] for x in ast.walk(node)
                              if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                              and x.func.attr in BLOCKED_METHODS})
                size = node.end_lineno - node.lineno + 1
                if blk:
                    rows.append((rel, name, "BLOCKED", blk, size)); continue
                local = bound_inside(node)
                miss = []
                for x in ast.walk(node):
                    if isinstance(x, ast.Call) and isinstance(x.func, ast.Name):
                        nm = x.func.id
                        if nm in local or nm in mirror_modlevel or nm in dir(builtins): continue
                        cand = live_defs.get(nm, [])
                        if cand and int_shaped(cand[0][1]): continue   # (r4): int-shaped is free
                        miss.append(nm)
                # (o4) COMPLETED, gen #32: the walk must cover SELF-METHOD callees too, not only free
                # functions. A `self.<m>()` whose `<m>` the DESTINATION mirror file does not define
                # auto-synthesizes a RECEIVER-LESS abstract `val self__<m>_<n>` with an unconstrained
                # result — the same (l4)/(n4) migration, arrived at from the callee side. Adding this
                # check moved FORTY markers out of CLEAR; the commonest missing self-methods are
                # `self.generic_visit` (8), `self._expr_to_whyml` (4),
                # `self._emitting_compute_return_type` (4) and `self._emitting_build_param_list` (4).
                # (An earlier revision of this comment cited `ConcurrencyChecker._check_function` as
                # the motivating case. That was WRONG — the mirror DOES define `_walk_body`, at line
                # 65; I had concluded its absence from a `grep` window that only showed defs within
                # five lines of a marker. The check is right, the example was not. Lesson (s4).)
                own = mirror_methods.get(rel, set())
                for x in ast.walk(node):
                    if (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                            and isinstance(x.func.value, ast.Name) and x.func.value.id == "self"
                            and x.func.attr not in own):
                        miss.append("self." + x.func.attr)
                if miss:
                    rows.append((rel, name, "NET-ZERO", sorted(set(miss)), size)); continue
                rows.append((rel, name, "CLEAR", [], size))

    c = collections.Counter(r[2] for r in rows)
    print("[*] preflight-marker-callee-closure: %d marker(s) — %s"
          % (len(rows), ", ".join(f"{k} {v}" for k, v in sorted(c.items()))))
    b = collections.Counter(x for r in rows if r[2] == "BLOCKED" for x in r[3])
    print("    BLOCKED by: " + ", ".join(f"{k} {v}" for k, v in b.most_common()))
    nz = collections.Counter(x for r in rows if r[2] == "NET-ZERO" for x in r[3])
    print("    NET-ZERO missing callees: " + ", ".join(f"{k} {v}" for k, v in nz.most_common(8)))

    if args.join or args.list_clear:
        clear = []
        for rel, name, v, _x, size in rows:
            if v != "CLEAR": continue
            qn = next((q for (f2, q) in reasons if f2 == rel and q.rsplit(".", 1)[-1] == name), None)
            cls = reasons.get((rel, qn)) if qn else None
            if cls in (None, "unclassified"): clear.append((size, rel, qn or name))
        print("\n[*] CLEAR and UNCLASSIFIED (the shortlist, smallest live body first): **%d**"
              % len(clear))
        print("    NECESSARY, NOT SUFFICIENT — the int-erasure seam is type-shaped and invisible here.")
        if args.list_clear:
            for size, rel, qn in sorted(clear):
                print(f"   {size:5d} lines  {rel}::{qn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
