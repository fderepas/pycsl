"""raisesfix.py <mirror-relpath> <ExcName> [max_iters] — the #19 fixpoint device, for
`#@ raises`. Reads Why3's `this expression raises unlisted exception <E>`, maps the
reported .mlw line back to its enclosing `let <cls>__<meth>`, and adds `#@ raises <E>` to
that mirror method. Repeats until L3-tc is green."""
import ast, os, re, subprocess, sys
rel, EXC = sys.argv[1], sys.argv[2]
MAXIT = int(sys.argv[3]) if len(sys.argv) > 3 else 40
P = os.path.join("src/self-annotate/src", rel)
MLW = P[:-3] + ".mlw"
ENV = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"],
           PYTHONHASHSEED="0")

def emit():
    r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", P, "--import-path", "src/pycsl",
                        "--no-proof", "--keep-mlw"], capture_output=True, text=True, env=ENV,
                       timeout=600)
    return r.stdout + r.stderr

def enclosing(lineno):
    L = open(MLW).read().split("\n")
    for i in range(min(lineno, len(L)) - 1, -1, -1):
        m = re.match(r"^  (?:let rec|let|with|val)\s+([A-Za-z_0-9]+)", L[i])
        if m:
            return m.group(1)
    return None

def mirror_method(wn):
    tree = ast.parse(open(P).read())
    best = None
    def walk(scope, cls):
        nonlocal best
        for n in scope:
            if isinstance(n, ast.ClassDef):
                walk(n.body, n.name)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if wn == ((cls.lower() + "__" + n.name) if cls else n.name):
                    best = (cls, n.name)
    walk(tree.body, None)
    return best

def add_raises(cls, name):
    lines = open(P).read().split("\n")
    tree = ast.parse("\n".join(lines))
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
    ind = None
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            break
        b0 = i
        i -= 1
    for k in range(b0, first):
        st = lines[k].strip()
        if st.startswith("#@ raises") and EXC in st:
            return False
        if ind is None and st.startswith("#@"):
            ind = lines[k][:len(lines[k]) - len(lines[k].lstrip())]
    if ind is None:
        ind = lines[first][:len(lines[first]) - len(lines[first].lstrip())]
    lines.insert(first, ind + "#@ raises " + EXC + " when True")
    open(P, "w").write("\n".join(lines))
    return True

seen = []
for it in range(MAXIT):
    out = emit()
    if "L3-tc ✓" in out:
        print(f"GREEN after {it} iteration(s); touched {len(seen)} method(s):")
        for x in seen:
            print("   ", x)
        sys.exit(0)
    ln = None
    for mm in re.finditer(r'File "[^"]*", line (\d+), characters [^\n]*\n([^\n]*)', out):
        if "unlisted exception" in mm.group(2):
            ln = int(mm.group(1))
            break
    if ln is None:
        print("STOP: not an unlisted-exception error ->", out.strip().split("\n")[-1][:200])
        print("touched:", seen)
        sys.exit(1)
    wn = enclosing(ln)
    tgt = mirror_method(wn) if wn else None
    if tgt is None or not add_raises(*tgt):
        print(f"STOP at {wn!r} / {tgt}")
        print("touched:", seen)
        sys.exit(1)
    seen.append(f"{tgt[0]}.{tgt[1]}")
    print(f"  it{it}: + #@ raises {EXC} on {tgt[0]}.{tgt[1]}")
print("STOP: iteration cap; touched:", len(seen))
sys.exit(1)
