"""Route #144 census: @dataclass classes and their CONSTRUCTION sites.
Reports, per construction site, whether the repair (prepend base dataclass fields in
MRO order, drop ClassVars) CHANGES the model's positional binding."""
import ast, os, sys, json, collections

def is_dataclass_dec(node):
    for d in node.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Name) and f.id == "dataclass":
            return True
        if isinstance(f, ast.Attribute) and f.attr == "dataclass":
            return True
    return False

def ann_is_classvar(ann):
    if ann is None:
        return False
    base = ann.value if isinstance(ann, ast.Subscript) else ann
    if isinstance(base, ast.Name):
        return base.id == "ClassVar"
    if isinstance(base, ast.Attribute):
        return base.attr == "ClassVar"
    return False

def ann_is_initvar(ann):
    if ann is None:
        return False
    base = ann.value if isinstance(ann, ast.Subscript) else ann
    if isinstance(base, ast.Name):
        return base.id == "InitVar"
    if isinstance(base, ast.Attribute):
        return base.attr == "InitVar"
    return False

def base_names(node):
    out = []
    for b in node.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
    return out

def scan_file(path):
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        return None
    classes = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        has_init = any(isinstance(c, ast.FunctionDef) and c.name == "__init__"
                       for c in node.body)
        anns = [(s.target.id, ann_is_classvar(s.annotation), ann_is_initvar(s.annotation))
                for s in node.body
                if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
        classes[node.name] = {
            "dc": is_dataclass_dec(node), "has_init": has_init,
            "bases": base_names(node), "anns": anns, "line": node.lineno,
        }
    return tree, classes

def model_params(cls):
    """current model init_params for a dataclass w/o explicit __init__"""
    return [n for n, cv, iv in cls["anns"]]

def repaired_params(name, classes, seen=None):
    """base dataclass fields (MRO-ish, base first), ClassVars dropped, redeclaration
    keeps the base position."""
    if seen is None:
        seen = set()
    if name in seen or name not in classes:
        return []
    seen.add(name)
    cls = classes[name]
    out = []
    for b in cls["bases"]:
        bc = classes.get(b)
        if bc is None or not bc["dc"] or bc["has_init"]:
            continue
        for p in repaired_params(b, classes, seen):
            if p not in out:
                out.append(p)
    for n, cv, iv in cls["anns"]:
        if cv:
            continue
        if n not in out:
            out.append(n)
    return out

TREES = sys.argv[1:]
rows = []
affected_classes = []
for tree_root in TREES:
    for dirpath, dirnames, filenames in os.walk(tree_root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".venv")]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            r = scan_file(p)
            if r is None:
                continue
            tree, classes = r
            # dataclasses with no explicit __init__ whose params would move
            moved_classes = {}
            for cname, cls in classes.items():
                if not cls["dc"] or cls["has_init"]:
                    continue
                cur = model_params(cls)
                rep = repaired_params(cname, classes)
                if cur != rep:
                    moved_classes[cname] = (cur, rep)
                    affected_classes.append((p, cname, cur, rep))
            if not moved_classes:
                continue
            # construction sites
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if nm not in moved_classes:
                    continue
                cur, rep = moved_classes[nm]
                npos = len(node.args)
                kws = [k.arg for k in node.keywords if k.arg]
                # current binding
                def binding(params):
                    if not params:
                        return {}
                    if not (npos and npos <= len(params)) and not kws:
                        return {}
                    b = {params[i]: ("pos%d" % i) for i in range(min(npos, len(params)))}
                    for k in kws:
                        if k in params:
                            b[k] = "kw:" + k
                    return b
                bc_, br_ = binding(cur), binding(rep)
                rows.append({
                    "file": p, "line": node.lineno, "cls": nm, "npos": npos,
                    "kws": kws, "cur_params": cur, "rep_params": rep,
                    "changes": bc_ != br_,
                })
print(json.dumps({"classes": affected_classes, "sites": rows}, indent=1))
