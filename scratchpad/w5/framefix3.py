"""framefix3.py <mirror.py-relpath> [max_iters]

#32 avatar-frame fixpoint. Same #19 device (drive `#@ assigns` against Why3's OWN error
text as a LOOP), but the field set is DERIVED PER METHOD from the LIVE transitive self-write
closure that `bin/check-trusted-frame-honesty.py` already computes — not a blanket list.
Handles the `_pyobj_state` rejection the avatar-frame rule produces:
    "this expression depends on variable _pyobj_state, which is left out in the specification"
"""
import ast, importlib.util, os, re, subprocess, sys

ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location(
    "fh", os.path.join(ROOT, "bin", "check-trusted-frame-honesty.py"))
fh = importlib.util.module_from_spec(spec)
sys.argv = ["fh"]
spec.loader.exec_module(fh)

rel = sys.argv0 if False else None
rel = os.environ["FF_REL"]
MAXIT = int(os.environ.get("FF_MAX", "60"))
P = os.path.join("src/self-annotate/src", rel)
MLW = P[:-3] + ".mlw"
ENV = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"],
           PYTHONHASHSEED="0")

classes, bases, funcs, tables = fh._parse_tree(fh.LIVE_ROOT)
direct, trans = fh._self_write_fixpoint(classes, bases, funcs, tables)


def emit():
    r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", P, "--import-path", "src/pycsl",
                        "--no-proof", "--keep-mlw"], capture_output=True, text=True, env=ENV,
                       timeout=900)
    return r.stdout + r.stderr


def enclosing(lineno):
    L = open(MLW).read().split("\n")
    for i in range(min(lineno, len(L)) - 1, -1, -1):
        m = re.match(r"^  (?:let rec|let|with|val)\s+([A-Za-z_0-9]+)", L[i])
        if m:
            return m.group(1)
    return None


def mirror_method(whyml_name):
    src = open(P).read()
    tree = ast.parse(src)
    best = None
    def walk(scope, cls):
        nonlocal best
        for n in scope:
            if isinstance(n, ast.ClassDef):
                walk(n.body, n.name)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                want = ((cls.lower() + "__" + n.name) if cls else n.name)
                if whyml_name == want:
                    best = (cls, n.name)
    walk(tree.body, None)
    return best


def live_writes(cls, name):
    for key, ws in trans.items():
        if key[-1] == name and (cls is None or key[-2] == cls or cls in key):
            return sorted(ws)
    return []


def merge(cls, name, fields):
    src = open(P).read()
    lines = src.split("\n")
    tree = ast.parse(src)
    target = None
    def walk(scope, c):
        nonlocal target
        for n in scope:
            if isinstance(n, ast.ClassDef):
                walk(n.body, n.name)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if n.name == name and c == cls:
                    target = n
    walk(tree.body, None)
    if target is None:
        return False
    first = min([d.lineno for d in target.decorator_list] + [target.lineno]) - 1
    i = first - 1
    b0 = first
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            break
        b0 = i
        i -= 1
    have = None
    ind = None
    for k in range(b0, first):
        st = lines[k].strip()
        if st.startswith("#@ assigns"):
            have = k
        if ind is None and st.startswith("#@"):
            ind = lines[k][:len(lines[k]) - len(lines[k].lstrip())]
    if ind is None:
        ind = lines[first][:len(lines[first]) - len(lines[first].lstrip())]
    cur = []
    if have is not None:
        txt = lines[have].strip()[len("#@ assigns"):].strip()
        if txt and txt != "\\nothing":
            cur = [x.strip() for x in txt.split(",") if x.strip()]
    new = sorted(set(cur) | {"self." + f for f in fields})
    if set(new) == set(cur) or not fields:
        return False
    line = ind + "#@ assigns " + ", ".join(new)
    if have is not None:
        lines[have] = line
    else:
        lines.insert(first, line)
    open(P, "w").write("\n".join(lines))
    return True


for it in range(MAXIT):
    out = emit()
    if "L3-tc ✓" in out:
        print(f"GREEN after {it} iteration(s)")
        sys.exit(0)
    ln = None
    for mm in re.finditer(r'File "[^"]*", line (\d+),[^\n]*\n((?:[^\n]*\n){0,2})', out):
        if "_pyobj_state" in mm.group(2) or "write effect" in mm.group(2):
            ln = int(mm.group(1)); msg = " ".join(mm.group(2).split())[:80]; break
    if ln is None:
        print("STOP: not a frame error ->", out.strip().split("\n")[-1][:200])
        sys.exit(1)
    wn = enclosing(ln)
    tgt = mirror_method(wn) if wn else None
    if tgt is None:
        print(f"STOP: cannot map emitted symbol {wn!r} at line {ln}")
        sys.exit(1)
    fields = live_writes(tgt[0], tgt[1])
    ok = merge(tgt[0], tgt[1], fields)
    print(f"  it{it}: {tgt[0]}.{tgt[1]} += {fields[:6]}{'...' if len(fields)>6 else ''} ({msg[:50]})"
          + ("" if ok else "  [NO CHANGE -> STOP]"))
    if not ok:
        sys.exit(1)
print("STOP: iteration cap")
sys.exit(1)
