"""Census for ROUTE #79's repair AS ACTUALLY SCOPED.

A field becomes `(any int)` only when BOTH hold:
  (1) the LAST top-level `self.f = rhs` in __init__ has an RHS that NAMES something
      outside the __init__ parameter set  (census class (iii) -- literal RHSs and
      param-only RHSs are excluded), and
  (2) the field's type is SCALAR -- the emitter's `_NONSCALAR` guard already excludes
      list/array/dict/set/frozenset/option, so the array arm cannot move.
Reports by root and by file, and separately the fields ALREADY covered by route #83
(nested stores) so the increment over HEAD is visible.
"""
import ast, os, sys, json

NONSCALAR = {"list", "array", "dict", "set", "frozenset", "option"}
ROOTS = ["test-suite/corpus", "src/self-annotate", "src/pycsl", "src/pycsl_lib"]

def ftype_from_ann(ann):
    try:
        s = ast.unparse(ann)
    except Exception:
        return "int"
    s = s.strip()
    low = s.lower()
    for t in ("list", "dict", "set", "frozenset", "optional", "sequence", "tuple"):
        if low.startswith(t):
            return "option" if t == "optional" else ("list" if t in ("sequence","tuple") else t)
    return "int"

def ftype_from_rhs(rhs):
    if isinstance(rhs, ast.Dict):  return "dict"
    if isinstance(rhs, ast.Set):   return "set"
    if isinstance(rhs, ast.List):  return "list"
    if isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name) \
       and rhs.func.id in ("set", "frozenset", "dict", "list"):
        return rhs.func.id
    return "int"

rows = []
for root in ROOTS:
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__", ".venv")]
        for fn in fns:
            if not fn.endswith(".py"): continue
            p = os.path.join(dp, fn)
            try:
                tree = ast.parse(open(p, encoding="utf-8", errors="replace").read())
            except Exception:
                continue
            for cls in ast.walk(tree):
                if not isinstance(cls, ast.ClassDef): continue
                for child in cls.body:
                    if not (isinstance(child, ast.FunctionDef) and child.name == "__init__"):
                        continue
                    pset = {a.arg for a in (child.args.posonlyargs + child.args.args
                                            + child.args.kwonlyargs) if a.arg != "self"}
                    # field types: first store wins, as _collect_class_fields does
                    ftypes, seen = {}, set()
                    for st in ast.walk(child):
                        tgt = rhs = ann = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1:
                            tgt, rhs = st.targets[0], st.value
                        elif isinstance(st, ast.AnnAssign):
                            tgt, rhs, ann = st.target, st.value, st.annotation
                        if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self"):
                            continue
                        if tgt.attr in seen: continue
                        seen.add(tgt.attr)
                        ftypes[tgt.attr] = ftype_from_ann(ann) if ann is not None else \
                                           (ftype_from_rhs(rhs) if rhs is not None else "int")
                    # route #83 set: nested stores
                    top_ids = {id(s) for s in child.body}
                    nested = set()
                    for st in ast.walk(child):
                        if id(st) in top_ids: continue
                        tgt = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1: tgt = st.targets[0]
                        elif isinstance(st, ast.AnnAssign): tgt = st.target
                        if (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self"):
                            nested.add(tgt.attr)
                    # last top-level store class per field
                    last = {}
                    for st in child.body:
                        tgt = rhs = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1:
                            tgt, rhs = st.targets[0], st.value
                        elif isinstance(st, ast.AnnAssign) and st.value is not None:
                            tgt, rhs = st.target, st.value
                        if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self"):
                            continue
                        names = {n.id for n in ast.walk(rhs) if isinstance(n, ast.Name)}
                        if not names:
                            cls_ = "literal"
                        elif (names & pset) and names <= pset:
                            cls_ = "captured"
                        else:
                            cls_ = "outside"          # <-- route #79 proper
                        last[tgt.attr] = cls_
                    for f, c in last.items():
                        if c != "outside": continue
                        t = ftypes.get(f, "int")
                        rows.append({"root": root, "file": p, "cls": cls.name, "field": f,
                                     "ftype": t, "scalar": t not in NONSCALAR,
                                     "already83": f in nested})
                    break

moves = [r for r in rows if r["scalar"] and not r["already83"]]
print("route#79 class-(iii) sites total          :", len(rows))
print("  of which SCALAR (emitter would move)    :", len([r for r in rows if r['scalar']]))
print("  already unknown via route #83 (nested)  :", len([r for r in rows if r['scalar'] and r['already83']]))
print("  NEW sites this repair makes unconstrained:", len(moves))
print()
from collections import Counter
print("NEW sites by root:", dict(Counter(r["root"] for r in moves)))
print("NEW sites by ftype:", dict(Counter(r["ftype"] for r in moves)))
print()
print("--- NEW sites in test-suite/corpus (the byte-diff risk) ---")
for r in moves:
    if r["root"] == "test-suite/corpus":
        print("   ", r["file"], r["cls"] + "." + r["field"])
print()
print("--- NEW sites in src/self-annotate (the whole-file-proof cost) ---")
c = Counter(r["file"] for r in moves if r["root"] == "src/self-annotate")
for f, n in c.most_common():
    print("   %3d  %s" % (n, f))
json.dump(rows, open("scratchpad/w60/r79_census2.json", "w"), indent=1)
