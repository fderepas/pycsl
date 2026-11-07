#!/usr/bin/env python3
"""census.py <tree> <prefilter.tsv> [filter...] : for each MUT row: port live body verbatim + live sig
(scratch tree only), emit --no-proof; while the first blocker is an in-place-mutator refusal,
neutralise THAT mutator (statement -> pass; expression pop/setdefault -> read) and re-emit.
Record chain + final blocker. Always restores the file."""
import ast, os, re, subprocess, sys
tree, tsv = sys.argv[1], sys.argv[2]
filt = sys.argv[3:]
PY = "/home/fabrice/git/pycsl/.venv/bin/python3"
S = os.path.dirname(os.path.abspath(__file__))
SIGFIX = "/tmp/claude-1000/-home-fabrice-git-pycsl/7bdb4936-b536-4d12-86b7-7ad1b607106c/scratchpad/ch14/census/sigfix.py"
env = dict(os.environ, PYTHONHASHSEED="0")
rows = [l.rstrip("\n").split("\t") for l in open(tsv) if l.startswith("MUT\t")]
ONLY = os.environ.get("ONLY")
if ONLY: rows = [r for r in rows if r[2] in ONLY.split(",")]
MUTRE = re.compile(r"`([^`]*)\.(\w+)\(\.\.\.\)` (?:MUTATES its receiver in place|appends to the collection in the field)")

def find_fn(src, q):
    t = ast.parse(src); hits = []
    def walk(n, pre):
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qq = pre + c.name
                if qq == q: hits.append(c)
                walk(c, qq + ".")
            elif isinstance(c, ast.ClassDef): walk(c, pre + c.name + ".")
            else: walk(c, pre)
    walk(t, ""); return hits[0] if hits else None

def neutralise(path, q, recv, meth):
    src = open(path).read(); lines = src.split("\n")
    fn = find_fn(src, q)
    if fn is None: return "nofn"
    cands = []
    for st in ast.walk(fn):
        if not isinstance(st, ast.stmt) or st is fn: continue
        for c in ast.walk(st):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == meth:
                cands.append((st, c))
    # innermost statement per call: keep the stmt with the smallest span
    best = {}
    for st, c in cands:
        k = id(c)
        if k not in best or (st.end_lineno - st.lineno) < (best[k][0].end_lineno - best[k][0].lineno):
            best[k] = (st, c)
    cands = list(best.values())
    exact = [x for x in cands if ast.unparse(x[1].func.value).replace(" ", "") == recv.replace(" ", "")]
    pick = (exact or cands)
    if not pick: return "nocall"
    st, c = sorted(pick, key=lambda x: (x[1].lineno, x[1].col_offset))[0]
    tag = "exact" if exact else "attr-only"
    if isinstance(st, ast.Expr) or (isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign)) is False and isinstance(st, ast.Expr)):
        ind = lines[st.lineno - 1][:st.col_offset]
        lines[st.lineno - 1:st.end_lineno] = [ind + "pass  # NEUTRALISED " + meth]
        open(path, "w").write("\n".join(lines)); return f"stmt:{tag}"
    # expression position
    r = ast.unparse(c.func.value); a = [ast.unparse(x) for x in c.args]
    if meth == "pop":
        rep = f"{r}[-1]" if not a else (f"{r}[{a[0]}]" if len(a) == 1 else f"{r}.get({a[0]}, {a[1]})")
    elif meth == "setdefault":
        rep = f"{r}[{a[0]}]" if len(a) == 1 else f"{r}.get({a[0]}, {a[1]})"
    else:
        # value-less mutator in an expression position: replace stmt by pass
        ind = lines[st.lineno - 1][:st.col_offset]
        lines[st.lineno - 1:st.end_lineno] = [ind + "pass  # NEUTRALISED " + meth]
        open(path, "w").write("\n".join(lines)); return f"stmt2:{tag}"
    if c.lineno != c.end_lineno:
        # multi-line call: rewrite the span
        first = lines[c.lineno - 1][:c.col_offset]; last = lines[c.end_lineno - 1][c.end_col_offset:]
        lines[c.lineno - 1:c.end_lineno] = [first + rep + last]
    else:
        L = lines[c.lineno - 1]; lines[c.lineno - 1] = L[:c.col_offset] + rep + L[c.end_col_offset:]
    open(path, "w").write("\n".join(lines)); return f"expr:{tag}"

def emit(f):
    r = subprocess.run([PY, "src/pycsl/pycsl.py", f, "--import-path", "src/pycsl", "--no-proof", "--keep-mlw"],
                       cwd=tree, capture_output=True, text=True, env=env, timeout=1800)
    return r.stdout + r.stderr

def diag(out):
    i = out.find("This expression has type")
    if i >= 0: return " ".join(out[i:i + 300].split())[:220]
    for l in out.split("\n"):
        if re.search(r"unbound|MUTATES|nested function|with \.\.\. as|not supported|refus|cannot|heterogeneous|rebound|Error|error", l) and not l.lstrip().startswith(("[*]", "[+]", "[level]")):
            return l.strip()[:220]
    return "?"

for _, rel, q, reason, muts in rows:
    if filt and not any(x in rel for x in filt): continue
    f = "src/self-annotate/src/" + rel; path = os.path.join(tree, f); orig = open(path).read()
    chain = []
    try:
        p = subprocess.run([PY, "bin/port-one-mirror-body.py", ".", rel, q, "--convert", "--replace"], cwd=tree, capture_output=True, text=True)
        if p.returncode != 0:
            print(f"NOPORT\t{rel}\t{q}\t{reason}\t\t{(p.stdout+p.stderr).strip().splitlines()[-1][:200]}", flush=True); continue
        subprocess.run([PY, SIGFIX, ".", rel, q], cwd=tree, capture_output=True, text=True)
        first = None
        for it in range(15):
            out = emit(f)
            if "L3-tc ✓" in out:
                print(f"{'TCOK' if chain else 'TCOK0'}\t{rel}\t{q}\t{reason}\t{';'.join(chain)}\tfirst={first}", flush=True); break
            m = MUTRE.search(out)
            if m:
                recv, meth = m.group(1), m.group(2)
                if first is None: first = "MUT"
                res = neutralise(path, q, recv, meth)
                chain.append(f"{recv}.{meth}[{res}]")
                if res in ("nofn", "nocall"):
                    print(f"STUCK\t{rel}\t{q}\t{reason}\t{';'.join(chain)}\t{diag(out)}", flush=True); break
                continue
            d = diag(out)
            if d == "?":
                open(os.path.join(S, "qout", (rel + "." + q).replace("/", "_") + ".out"), "w").write(out)
            if first is None: first = "OTHER"
            print(f"{'NEXT' if chain else 'OTHER0'}\t{rel}\t{q}\t{reason}\t{';'.join(chain)}\t{d}", flush=True)
            snap = os.path.join(S, "probes", (rel + "." + q).replace("/", "_") + ".py")
            os.makedirs(os.path.dirname(snap), exist_ok=True); open(snap, "w").write(open(path).read())
            break
        else:
            print(f"LOOP\t{rel}\t{q}\t{reason}\t{';'.join(chain)}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT\t{rel}\t{q}\t{reason}\t{';'.join(chain)}", flush=True)
    finally:
        open(path, "w").write(orig)
