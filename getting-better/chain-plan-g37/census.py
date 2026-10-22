#!/usr/bin/env python3
"""census.py (g37 ch32: FIRST-blocker variant of g36 chain.py; --first stops after locating the first blocker) <tree> <results.jsonl> [--budget SECS] [--only file::qual,...]

Blocker-CHAIN census (g36 plan). For each live `#@ \\trusted` row of trusted-reasons.tsv:
  port live body+signature into the mirror (scratch tree only, restored after),
  emit --no-proof --keep-mlw (through heavy.sh, QUICK class), record the FIRST blocker,
  LOCATE it to a statement of the ported body (front-end message pattern, or for a Why3
  type error an ANCHORED re-emit: an `_pycsl_anc = 10000NN` int store before every
  statement, mapped back from the .mlw error line), NEUTRALISE that statement with a
  type-correct placeholder, re-emit; up to 6 blocker rounds.
Appends one JSON object per row; resumable (rows already in results are skipped)."""
import ast, json, os, re, subprocess, sys, time

tree, RES = sys.argv[1], sys.argv[2]
BUDGET = 540
ONLY = None
a = sys.argv[3:]
if "--budget" in a: BUDGET = int(a[a.index("--budget") + 1])
if "--only" in a: ONLY = set(a[a.index("--only") + 1].split(","))
PURGE = "--purge" in a
FIRST = "--first" in a
if "--only-file" in a: ONLY = set(l.strip() for l in open(a[a.index("--only-file") + 1]) if l.strip())
PY = "/home/fabrice/git/pycsl/.venv/bin/python3"
HEAVY = "/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh"
env = dict(os.environ, PYTHONHASHSEED="0")
MAXROUNDS = 14
MAXEMITS = 36
ANC = "_pycsl_anc"
ANC0 = 7300000
T0 = time.time()

# ------------------------------------------------------------------ rows
rows = []
for l in open(os.path.join(tree, "getting-better/trusted-reasons.tsv")):
    if l.startswith("#") or not l.strip(): continue
    c = l.rstrip("\n").split("\t")
    if c[0] == "file": continue
    rows.append((c[0], c[1], c[2]))
done = set()
if os.path.exists(RES):
    for l in open(RES):
        try:
            j = json.loads(l); done.add((j["file"], j["qual"]))
        except Exception: pass


def defs_named(src_tree, qual):
    """all defs with this qualname, in source order; returns (node, ancestors)"""
    base = qual.split("#")[0]
    hits = []
    def walk(n, pre, anc):
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = pre + c.name
                if q == base: hits.append((c, anc))
                walk(c, q + ".", anc + [c])
            elif isinstance(c, ast.ClassDef):
                walk(c, pre + c.name + ".", anc + [c])
            else:
                walk(c, pre, anc)
    walk(src_tree, "", [])
    hits.sort(key=lambda h: h[0].lineno)
    return hits


def pick(src_tree, qual):
    hits = defs_named(src_tree, qual)
    k = int(qual.split("#")[1]) - 1 if "#" in qual else 0
    return hits[k] if 0 <= k < len(hits) else (None, None)


def body_wo_doc(fn):
    b = list(fn.body)
    if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) and isinstance(b[0].value.value, str):
        b = b[1:]
    return b

# ------------------------------------------------------------------ pre-skip classes
EFFECT = re.compile(r"\bsubprocess\.|\bos\.(makedirs|remove|unlink|rename|replace|rmdir|mkdir)\b|\.mkdir\(|\.write_text\(|\.write_bytes\(|\.unlink\(|shutil\.|\bos\.environ\[[^\]]*\]\s*=")


def raise_only(fn):
    b = body_wo_doc(fn)
    return bool(b) and all(isinstance(s, ast.Raise) for s in b)


def precheck(rel, qual, reason, trusted_quals):
    mp = os.path.join(tree, "src/self-annotate/src", rel)
    lp = os.path.join(tree, "src/pycsl", rel)
    if reason.startswith("correctness:"):
        return "SKIP-CORRECTNESS", None
    if not os.path.exists(lp): return "SKIP-NOLIVE", "no live file"
    msrc = open(mp).read(); lsrc = open(lp).read()
    m, manc = pick(ast.parse(msrc), qual)
    l, lanc = pick(ast.parse(lsrc), qual)
    if m is None: return "SKIP-NOMIRRORDEF", None
    if l is None: return "SKIP-NOLIVE", "no live def"
    # nested inside a trusted encloser
    fn_anc = [x for x in manc if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if fn_anc:
        # qualname of the innermost function ancestor
        parts = qual.split("#")[0].split(".")
        encl = ".".join(parts[:-1])
        if any(t.split("#")[0] == encl for t in trusted_quals.get(rel, ())):
            return "SKIP-NESTED-IN-TRUSTED", encl
        return None, None
    lbody = ast.get_source_segment(lsrc, l) or ""
    if EFFECT.search(lbody):
        return "SKIP-DNC-EFFECT", EFFECT.search(lbody).group(0)
    if raise_only(l):
        return "SKIP-DNC-RAISEONLY", None
    return None, None

# ------------------------------------------------------------------ port


def port(rel, qual):
    mp = os.path.join(tree, "src/self-annotate/src", rel)
    lp = os.path.join(tree, "src/pycsl", rel)
    msrc = open(mp).read(); lsrc = open(lp).read()
    ml = msrc.split("\n"); ll = lsrc.split("\n")
    m, _ = pick(ast.parse(msrc), qual); l, _ = pick(ast.parse(lsrc), qual)
    mi = len(ml[m.lineno - 1]) - len(ml[m.lineno - 1].lstrip())
    li = len(ll[l.lineno - 1]) - len(ll[l.lineno - 1].lstrip())
    new = []
    for x in ll[l.lineno - 1:l.end_lineno]:
        if not x.strip(): new.append(""); continue
        if mi >= li: new.append(" " * (mi - li) + x)
        else: new.append(x[li - mi:] if x[:li - mi].strip() == "" else x.lstrip())
    first = (min(d.lineno for d in m.decorator_list) if m.decorator_list else m.lineno) - 1
    out = ml[:m.lineno - 1] + new + ml[m.end_lineno:]
    i = first - 1; killed = None
    while i >= 0 and (not out[i].strip() or out[i].lstrip().startswith("#")):
        if out[i].lstrip().startswith("#@ \\trusted"):
            killed = i; break
        i -= 1
    if killed is None: return "nomarker"
    del out[killed]
    open(mp, "w").write("\n".join(out))
    return "ok"

# ------------------------------------------------------------------ emit


def emit(f):
    r = subprocess.run([HEAVY, PY, "src/pycsl/pycsl.py", f, "--import-path", "src/pycsl", "--no-proof", "--keep-mlw"],
                       cwd=tree, capture_output=True, text=True, env=env, timeout=900)
    return r.stdout + "\n" + r.stderr


_DUMPN = [0]
def parse_out(out):
    if "L3-tc ✓" in out: return {"ok": True}
    if os.environ.get("DUMP"):
        _DUMPN[0] += 1; open(os.path.join(os.environ["DUMP"], "out%03d.txt" % _DUMPN[0]), "w").write(out)
    m = re.search(r'(?m)^File "([^"]+\.mlw)", line (\d+), characters (\d+)-(\d+):\s*\n(.*?)(?=\n(?:Warning|File|\[)|\Z)', out, re.S)
    m2 = re.search(r'(?m)^File "([^"]+\.mlw)", line (\d+), character (\d+) to line (\d+), character (\d+):\s*\n(.*?)(?=\n(?:Warning|File|\[)|\Z)', out, re.S)
    if m2 and (not m or m2.start() < m.start()):
        msg = " ".join(m2.group(6).split())
        mlw = m2.group(1)
        if not os.path.isabs(mlw): mlw = os.path.join(tree, mlw)
        return {"ok": False, "kind": "why3", "mlw": mlw, "line": int(m2.group(2)), "c0": int(m2.group(3)),
                "c1": 10**6, "multiline": True, "msg": msg[:400]}
    if m:
        msg = " ".join(m.group(5).split())
        mlw = m.group(1)
        if not os.path.isabs(mlw): mlw = os.path.join(tree, mlw)
        return {"ok": False, "kind": "why3", "mlw": mlw, "line": int(m.group(2)), "c0": int(m.group(3)),
                "c1": int(m.group(4)), "msg": msg[:400]}
    i = out.find("[!] PIPELINE ERROR:")
    if i >= 0:
        msg = " ".join(out[i + 19:i + 1200].split())
        return {"ok": False, "kind": "fe", "msg": msg[:600]}
    for l in out.split("\n"):
        if l.lstrip().startswith(("Warning", "[*]", "[+]", "[level]", "[!] warning")): continue
        if re.search(r"Error|error|refus|not supported", l):
            return {"ok": False, "kind": "fe", "msg": l.strip()[:600]}
    return {"ok": False, "kind": "unknown", "msg": out[-600:]}


def mlw_block(lines, ln):
    """(start, end) 0-based line idx of the top-level decl containing 1-based line ln"""
    TOP = re.compile(r"^  (let|with|val|predicate|function|type|axiom|lemma|exception|use|clone|constant|scope|goal|meta)\b")
    s = ln - 1
    while s > 0 and not TOP.match(lines[s]): s -= 1
    e = ln
    while e < len(lines) and not TOP.match(lines[e]) and not lines[e].startswith("end"): e += 1
    return s, e


def block_name(line):
    m = re.match(r"^  (?:let|with|val)\s+(?:rec\s+)?(?:ghost\s+)?(?:function\s+|predicate\s+)?(\w+)", line)
    return m.group(1) if m else line.strip()[:40]

# ------------------------------------------------------------------ statement paths


def stmt_lists(node):
    for fld in ("body", "orelse", "finalbody"):
        v = getattr(node, fld, None)
        if isinstance(v, list) and v and isinstance(v[0], ast.stmt): yield fld, v
    for k, h in enumerate(getattr(node, "handlers", []) or []):
        yield f"handlers{k}", h.body
    for k, c in enumerate(getattr(node, "cases", []) or []):
        yield f"cases{k}", c.body


def all_stmts(fn):
    """[(path, stmt)] in source order (pre-order), excluding the docstring and nested defs' insides"""
    out = []
    def rec(lst, pre):
        for i, s in enumerate(lst):
            p = pre + ((i,),)
            out.append((p, s))
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
            for fld, sub in stmt_lists(s):
                rec(sub, p + ((fld,),))
    b = list(fn.body)
    rec(b, ())
    return out


def anchored_body(fn, src_lines, indent):
    """unparse the function body with an anchor store before every statement; returns (lines, {id: lineno-of-stmt})"""
    amap = {}
    cnt = [0]
    def anc_list(lst):
        new = []
        for s in lst:
            isdoc = isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)
            if not isdoc:
                cnt[0] += 1
                aid = ANC0 + cnt[0]
                amap[aid] = s.lineno
                a = ast.parse(f"{ANC} = {aid}").body[0]
                new.append(a)
            if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for fld in ("body", "orelse", "finalbody"):
                    v = getattr(s, fld, None)
                    if isinstance(v, list) and v and isinstance(v[0], ast.stmt):
                        setattr(s, fld, anc_list(v))
                for h in getattr(s, "handlers", []) or []: h.body = anc_list(h.body)
                for c in getattr(s, "cases", []) or []: c.body = anc_list(c.body)
            new.append(s)
        return new
    import copy
    f2 = copy.deepcopy(fn)
    f2.body = anc_list(f2.body)
    txt = []
    for s in f2.body:
        for x in ast.unparse(s).split("\n"):
            txt.append(" " * indent + x)
    return txt, amap


def locate_why3(rel, qual, path, err):
    """anchored re-emit; returns (stmt_lineno or None, info)"""
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    b = fn.body
    ind = len(L[b[0].lineno - 1]) - len(L[b[0].lineno - 1].lstrip())
    first = min(x.lineno for x in [b[0]] + [d for d in getattr(b[0], "decorator_list", [])]) - 1
    last = fn.end_lineno
    try:
        body, amap = anchored_body(fn, L, ind)
    except Exception as e:
        return None, {"anc": f"unparse-fail {e}"}
    open(path, "w").write("\n".join(L[:first] + body + L[last:]))
    try:
        out = emit("src/self-annotate/src/" + rel)
    finally:
        open(path, "w").write(src)
    p = parse_out(out)
    return locate_from(p, amap, err)


def emit_anchored(rel, qual, path):
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    b = fn.body
    ind = len(L[b[0].lineno - 1]) - len(L[b[0].lineno - 1].lstrip())
    first = b[0].lineno - 1
    last = fn.end_lineno
    try:
        body, amap = anchored_body(fn, L, ind)
    except Exception as e:
        return None, None
    open(path, "w").write("\n".join(L[:first] + body + L[last:]))
    try:
        out = emit("src/self-annotate/src/" + rel)
    finally:
        open(path, "w").write(src)
    return out, amap


def locate_from(p, amap, err):
    info = {}
    if p.get("ok"):
        return None, {"anc": "anchored-emit-OK(?)"}
    if p.get("kind") != "why3":
        return None, {"anc": "anchored-not-why3: " + p.get("msg", "")[:120]}
    info["anc_same"] = (err is None) or (p["msg"][:80] == err["msg"][:80])
    ml = open(p["mlw"]).read().split("\n")
    s, e = mlw_block(ml, p["line"])
    blk = ml[s:e]
    info["block"] = block_name(ml[s])
    best = None
    for k in range(s, p["line"]):
        for mm in re.finditer(r"\b(73\d{5})\b", ml[k]):
            aid = int(mm.group(1))
            if aid in amap and (k < p["line"] - 1 or mm.start() <= p["c0"]):
                best = aid
    has_any = any(re.search(r"\b73\d{5}\b", x) for x in blk)
    if best is None:
        info["anc"] = "error-outside-anchors" if not has_any else "before-first-anchor"
        info["errline"] = ml[p["line"] - 1].strip()[:200]
        if has_any and amap:
            best = min(amap)  # error in the hoisted decls: attribute to the first statement
            info["anc"] = "decl-area"
        else:
            return None, info
    info["anc"] = info.get("anc", "ok")
    info["snip"] = ml[p["line"] - 1][p["c0"]:p["c1"]][:160]
    info["errline"] = ml[p["line"] - 1].strip()[:200]
    # hoisted ref decls of the anchored block (types of locals)
    decls = {}
    for x in blk:
        mm = re.match(r"\s*let (\w+) = ref (.*) in\s*$", x)
        if mm: decls[mm.group(1)] = mm.group(2)
    info["decls"] = decls
    return amap[best], info


FEPAT = [
    (re.compile(r"`([^`]*)\.(\w+)\(\.\.\.\)` (?:MUTATES|appends to the collection)"), "call"),
    (re.compile(r"nested function '(\w+)'"), "nested"),
    (re.compile(r"with \.\.\. as"), "with"),
    (re.compile(r"`except (\w+)`|exception object|except .* as"), "try"),
    (re.compile(r"IDENTITY test against a `bool` literal"), "isbool"),
    (re.compile(r"'(\w+)' constructs an object"), "ctor"),
    (re.compile(r"rebound after|REBOUND"), "rebind"),
    (re.compile(r"heterogeneous"), "hetero"),
]


def innermost_stmt(fn, node):
    best = None
    for p, s in all_stmts(fn):
        if s.lineno <= node.lineno and s.end_lineno >= getattr(node, "end_lineno", node.lineno):
            if isinstance(s, (ast.If, ast.For, ast.While, ast.With, ast.Try)) and not hdr_contains(s, node):
                # node is inside the compound's body, deeper stmt will match
                pass
            if best is None or (s.end_lineno - s.lineno) <= (best.end_lineno - best.lineno):
                best = s
    return best


def hdr_contains(s, node):
    hs = []
    if isinstance(s, (ast.If, ast.While)): hs = [s.test]
    elif isinstance(s, ast.For): hs = [s.iter, s.target]
    elif isinstance(s, ast.With): hs = [i.context_expr for i in s.items]
    for h in hs:
        for x in ast.walk(h):
            if x is node: return True
    return False


def locate_fe(path, qual, msg):
    src = open(path).read()
    fn, _ = pick(ast.parse(src), qual)
    for rx, kind in FEPAT:
        m = rx.search(msg)
        if not m: continue
        if kind == "call":
            recv, meth = m.group(1), m.group(2)
            cs = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == meth]
            ex = [c for c in cs if ast.unparse(c.func.value).replace(" ", "") == recv.replace(" ", "")]
            cs = ex or cs
            if cs:
                c = sorted(cs, key=lambda c: (c.lineno, c.col_offset))[0]
                return innermost_stmt(fn, c), kind
        elif kind == "nested":
            nm = m.group(1)
            for x in ast.walk(fn):
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x is not fn and nm.endswith(x.name):
                    return x, kind
            for x in ast.walk(fn):
                if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and x is not fn:
                    return (x if isinstance(x, ast.stmt) else innermost_stmt(fn, x)), kind
        elif kind == "with":
            for x in ast.walk(fn):
                if isinstance(x, ast.With) and any(i.optional_vars is not None for i in x.items): return x, kind
        elif kind == "try":
            for x in ast.walk(fn):
                if isinstance(x, ast.ExceptHandler) and (x.name or (m.groups() and m.group(1) and isinstance(x.type, ast.Name) and x.type.id == m.group(1))):
                    return x, "handler"
            for x in ast.walk(fn):
                if isinstance(x, ast.ExceptHandler): return x, "handler"
        elif kind == "isbool":
            for x in ast.walk(fn):
                if isinstance(x, ast.Compare) and any(isinstance(o, (ast.Is, ast.IsNot)) for o in x.ops) and any(isinstance(c, ast.Constant) and isinstance(c.value, bool) for c in x.comparators):
                    return innermost_stmt(fn, x), kind
        elif kind == "ctor":
            pass
        elif kind == "hetero":
            for x in ast.walk(fn):
                if isinstance(x, (ast.List, ast.Tuple)) and len({type(e).__name__ for e in x.elts}) > 1:
                    return innermost_stmt(fn, x), kind
    # generic: first quoted identifier that occurs in exactly some statement
    for nm in re.findall(r"[`'](\w[\w.]*)", msg):
        last = nm.split(".")[-1]
        for p, s in all_stmts(fn):
            if isinstance(s, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef)): continue
            seg = ast.get_source_segment(src, s) or ""
            if re.search(r"\b%s\b" % re.escape(last), seg):
                return s, "generic:" + nm
    return None, None

# ------------------------------------------------------------------ neutralise


def ann_placeholder(ann):
    if ann is None: return None
    t = ast.unparse(ann).replace("typing.", "")
    t0 = re.split(r"[\[\]]", t)[0].strip().strip("'\"")
    if t0 in ("str",): return '""'
    if t0 in ("int",): return "0"
    if t0 in ("bool",): return "False"
    if t0 in ("float",): return "0.0"
    if t0 in ("List", "list", "Sequence", "Iterable"): return "[]"
    if t0 in ("Dict", "dict", "Mapping"): return "{}"
    if t0 in ("Set", "set", "FrozenSet", "frozenset"): return "set()"
    if t0 in ("Optional", "None") or t.endswith("| None") or t.startswith("None |"): return "None"
    if t0 in ("Tuple", "tuple"):
        inner = ann.slice if isinstance(ann, ast.Subscript) else None
        if inner is not None:
            elts = inner.elts if isinstance(inner, ast.Tuple) else [inner]
            ps = [ann_placeholder(e) or "None" for e in elts]
            return "(" + ", ".join(ps) + ("," if len(ps) == 1 else "") + ")"
        return "()"
    return None


def decl_placeholder(init):
    if init is None: return None
    i = init.strip()
    if re.fullmatch(r"\(?-?\d+\)?", i): return "0"
    if i == '""': return '""'
    if i in ("false", "true"): return "False"
    if re.search(r"Array\.make \d+ 0\)?$", i) or i.startswith("(Array.make") and i.endswith(" 0)"): return "[]"
    return None


def guess_from_rhs(v, src):
    if isinstance(v, ast.JoinedStr): return '""'
    if isinstance(v, ast.Constant):
        return repr(v.value) if isinstance(v.value, (str, int, bool)) else None
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute):
        a = v.func.attr
        if a in ("strip", "lstrip", "rstrip", "join", "lower", "upper", "replace", "format", "rjust", "ljust", "removeprefix", "removesuffix"): return '""'
        if a in ("startswith", "endswith", "isidentifier", "isdigit", "isalpha", "isspace"): return "False"
        if a in ("count", "find", "index", "rfind"): return "0"
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
        if v.func.id in ("str", "repr"): return '""'
        if v.func.id in ("len", "int"): return "0"
        if v.func.id in ("bool", "isinstance", "hasattr", "any", "all"): return "False"
        if v.func.id in ("list", "sorted"): return "[]"
    if isinstance(v, (ast.Compare, ast.BoolOp)) or (isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.Not)): return "False"
    if isinstance(v, (ast.List, ast.ListComp)): return "[]"
    if isinstance(v, (ast.Dict, ast.DictComp)): return "{}"
    if isinstance(v, ast.BinOp) and any(isinstance(x, (ast.JoinedStr,)) or (isinstance(x, ast.Constant) and isinstance(x.value, str)) for x in (v.left, v.right)): return '""'
    return None


def neutralise(path, qual, stmt_lineno, info, ret_ph, kind_hint=None):
    """returns (action-string) or None"""
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    target = None; tpath = None
    for p, s in all_stmts(fn):
        if s.lineno == stmt_lineno and (target is None or (s.end_lineno - s.lineno) < (target.end_lineno - target.lineno)):
            target, tpath = s, p
    if target is None and kind_hint is not None:
        target = kind_hint
    if target is None: return None
    s = target
    ind = " " * s.col_offset
    seg = ast.get_source_segment(src, s) or ""

    def repl_lines(a, b, new):
        L[a - 1:b] = new
        open(path, "w").write("\n".join(L))

    if isinstance(s, ast.ExceptHandler):
        # `except E as e:` -> `except E:` (e becomes unbound if read)
        hdr = L[s.lineno - 1]
        new = re.sub(r"\s+as\s+\w+\s*:", ":", hdr, count=1)
        if new == hdr:
            new = re.sub(r"except\b[^:]*:", "except Exception:", hdr, count=1)
        if new == hdr: return None
        L[s.lineno - 1] = new; open(path, "w").write("\n".join(L)); return "except-drop-as"
    if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) and s is not fn:
        # nested def: lift NOT attempted; replace the nested def body by its facade
        b0 = s.body[0]
        bi = " " * b0.col_offset
        ph = ann_placeholder(s.returns) or "None"
        repl_lines(b0.lineno, s.end_lineno, [bi + f"return {ph}  # NEUTRALISED nested"])
        return "nested-facade"
    if isinstance(s, (ast.If, ast.While)):
        t = s.test
        if t.lineno == t.end_lineno:
            line = L[t.lineno - 1]
            L[t.lineno - 1] = line[:t.col_offset] + "False" + line[t.end_col_offset:]
        else:
            first = L[t.lineno - 1][:t.col_offset]; last = L[t.end_lineno - 1][t.end_col_offset:]
            L[t.lineno - 1:t.end_lineno] = [first + "False" + last]
        open(path, "w").write("\n".join(L)); return "test->False"
    if isinstance(s, ast.For):
        it = s.iter
        first = L[it.lineno - 1][:it.col_offset]; last = L[it.end_lineno - 1][it.end_col_offset:]
        L[it.lineno - 1:it.end_lineno] = [first + "[]" + last]
        open(path, "w").write("\n".join(L)); return "iter->[]"
    if isinstance(s, ast.With):
        hdr0, hdr1 = s.lineno, s.body[0].lineno - 1
        nv = [ind + "if True:"]
        for it in s.items:
            if isinstance(it.optional_vars, ast.Name):
                pass
        repl_lines(hdr0, hdr1, nv)
        return "with->if True"
    if isinstance(s, ast.Try):
        return None
    if isinstance(s, ast.Return):
        if s.value is None: return None
        repl_lines(s.lineno, s.end_lineno, [ind + f"return {ret_ph}  # NEUTRALISED"])
        return f"return->{ret_ph}"
    if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        tgts = s.targets if isinstance(s, ast.Assign) else [s.target]
        if len(tgts) == 1 and isinstance(tgts[0], ast.Name):
            nm = tgts[0].id
            if isinstance(s, ast.AugAssign):
                repl_lines(s.lineno, s.end_lineno, [ind + "pass  # NEUTRALISED"]); return "aug->pass"
            ph = None
            if isinstance(s, ast.AnnAssign): ph = ann_placeholder(s.annotation)
            if ph is None: ph = decl_placeholder((info or {}).get("decls", {}).get(nm))
            if ph is None: ph = guess_from_rhs(s.value, src) if s.value is not None else None
            # other bindings of nm in the function?
            others = [x for x in ast.walk(fn) if isinstance(x, ast.Name) and x.id == nm and isinstance(x.ctx, ast.Store) and x is not tgts[0]]
            if ph is None and others:
                repl_lines(s.lineno, s.end_lineno, [ind + "pass  # NEUTRALISED"]); return "assign->pass(other-binding)"
            if ph is None:
                ann = ""
                repl_lines(s.lineno, s.end_lineno, [ind + "pass  # NEUTRALISED"]); return "assign->pass(UNBOUND-RISK)"
            if isinstance(s, ast.AnnAssign):
                repl_lines(s.lineno, s.end_lineno, [ind + f"{nm}: {ast.unparse(s.annotation)} = {ph}  # NEUTRALISED"])
            else:
                repl_lines(s.lineno, s.end_lineno, [ind + f"{nm} = {ph}  # NEUTRALISED"])
            return f"assign->{ph}"
        if len(tgts) == 1 and isinstance(tgts[0], ast.Tuple) and all(isinstance(e, ast.Name) for e in tgts[0].elts):
            # tuple unpack: keep names, give each a placeholder from decls (else 0)
            parts = []
            for e in tgts[0].elts:
                ph = decl_placeholder((info or {}).get("decls", {}).get(e.id)) or "0"
                parts.append(f"{ind}{e.id} = {ph}")
            repl_lines(s.lineno, s.end_lineno, [p + "  # NEUTRALISED" for p in parts]); return "unpack->phs"
        # subscript / attribute store
        repl_lines(s.lineno, s.end_lineno, [ind + "pass  # NEUTRALISED"]); return "store->pass"
    if isinstance(s, (ast.Expr, ast.Assert, ast.Raise, ast.Delete, ast.Global, ast.Nonlocal, ast.Pass, ast.Import, ast.ImportFrom)):
        if isinstance(s, ast.Pass): return None
        repl_lines(s.lineno, s.end_lineno, [ind + "pass  # NEUTRALISED"]); return type(s).__name__.lower() + "->pass"
    return None

def type_ph(t):
    t = t.strip()
    if t == "int": return "0"
    if t == "string": return '""'
    if t == "bool": return "False"
    if re.match(r"array\.Array\.array string", t): return '[""]'
    if re.match(r"array\.Array\.array int", t): return "[0]"
    if re.match(r"array\.Array\.array 'mu", t): return "[]"
    return None


def root_var_rewrite(path, qual, ent, msg):
    """a read of a local whose BINDING carries the wrong type: retarget the blocker to the binding"""
    mm = re.fullmatch(r"\(?!?(\w+)\)?", ent["snip"].strip())
    if not mm: return None
    x = mm.group(1)
    tm = re.search(r"has type (.*?), but is expected to have type (.*)$", msg)
    if not tm: return None
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    binds = [st for p_, st in all_stmts(fn) if isinstance(st, (ast.Assign, ast.AnnAssign))
             and any(isinstance(t, ast.Name) and t.id == x for t in (st.targets if isinstance(st, ast.Assign) else [st.target]))]
    if not binds: return None
    if any("# NEUTRALISED" in "\n".join(L[b.lineno - 1:b.end_lineno]) for b in binds): return "PH-CONFLICT"
    ph = type_ph(tm.group(2))
    if ph is None: return None
    first = binds[0]
    ent["root_var"] = x
    ent["use_stmt"] = ent.get("stmt")
    ent["stmt"] = ast.unparse(first)[:240]
    ent["root_rhs"] = ast.unparse(first.value)[:200] if first.value is not None else None
    for st in sorted(binds, key=lambda b: -b.lineno):
        ind = " " * st.col_offset
        if isinstance(st, ast.AnnAssign):
            L[st.lineno - 1:st.end_lineno] = [ind + f"{x}: {ast.unparse(st.annotation)} = {ph}  # NEUTRALISED root"]
        elif len(st.targets) == 1:
            L[st.lineno - 1:st.end_lineno] = [ind + f"{x} = {ph}  # NEUTRALISED root"]
        else:
            return None
    open(path, "w").write("\n".join(L))
    return f"root-var {x}->{ph} ({len(binds)} binding(s))"


def purge_var(path, qual, v, ret_ph):
    """PH conflict: remove every use of local v (simple stmt -> pass / return ph; compound header -> False / [])"""
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    edits = []
    for p_, st in all_stmts(fn):
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
        if isinstance(st, (ast.If, ast.While)):
            hs = [st.test]
        elif isinstance(st, ast.For):
            hs = [st.iter, st.target]
        elif isinstance(st, (ast.With, ast.Try)):
            continue
        else:
            hs = [st]
        if not any(isinstance(x, ast.Name) and x.id == v for h in hs for x in ast.walk(h)): continue
        edits.append(st)
    if not edits: return None
    for st in sorted(edits, key=lambda x: -x.lineno):
        ind = " " * st.col_offset
        if isinstance(st, (ast.If, ast.While)):
            t = st.test
            first = L[t.lineno - 1][:t.col_offset]; last = L[t.end_lineno - 1][t.end_col_offset:]
            L[t.lineno - 1:t.end_lineno] = [first + "False" + last]
        elif isinstance(st, ast.For):
            it = st.iter
            first = L[it.lineno - 1][:it.col_offset]; last = L[it.end_lineno - 1][it.end_col_offset:]
            L[it.lineno - 1:it.end_lineno] = [first + "[]" + last]
        elif isinstance(st, ast.Return) and st.value is not None:
            L[st.lineno - 1:st.end_lineno] = [ind + f"return {ret_ph}  # NEUTRALISED purge"]
        else:
            L[st.lineno - 1:st.end_lineno] = [ind + "pass  # NEUTRALISED purge"]
    open(path, "w").write("\n".join(L))
    return f"purge {v} ({len(edits)} stmt(s))"


def mut_expr_rewrite(path, qual, msg):
    m = FEPAT[0][0].search(msg)
    if not m: return None
    recv, meth = m.group(1), m.group(2)
    src = open(path).read(); L = src.split("\n")
    fn, _ = pick(ast.parse(src), qual)
    exprstmt_calls = {id(x.value) for x in ast.walk(fn) if isinstance(x, ast.Expr)}
    cs = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == meth
          and ast.unparse(c.func.value).replace(" ", "") == recv.replace(" ", "")]
    if not cs: return None
    c = sorted(cs, key=lambda c: (c.lineno, c.col_offset))[0]
    if id(c) in exprstmt_calls: return None
    r = ast.unparse(c.func.value); a = [ast.unparse(x) for x in c.args]
    if meth == "pop":
        rep = f"{r}[-1]" if not a else (f"{r}[{a[0]}]" if len(a) == 1 else f"{r}.get({a[0]}, {a[1]})")
    elif meth == "setdefault":
        rep = f"{r}[{a[0]}]" if len(a) == 1 else f"{r}.get({a[0]}, {a[1]})"
    elif meth == "popitem":
        rep = f"next(iter({r}.items()))"
    else:
        return None
    first = L[c.lineno - 1][:c.col_offset]; last = L[c.end_lineno - 1][c.end_col_offset:]
    L[c.lineno - 1:c.end_lineno] = [first + rep + last]
    open(path, "w").write("\n".join(L)); return f"mut-expr->{rep[:40]}"

# ------------------------------------------------------------------ facade check


def facade_check(rel, qual, lfn=None):
    """after TCOK: is the emitted body input-blind? looks for param names inside the emitted block"""
    path = os.path.join(tree, "src/self-annotate/src", rel)
    src = open(path).read()
    fn, _ = pick(ast.parse(src), qual)
    params = [a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs] + ([fn.args.vararg.arg] if fn.args.vararg else [])
    reads_self = any(isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name) and x.value.id == "self" for x in ast.walk(lfn or fn))
    mlwp = path[:-3] + ".mlw"
    if not os.path.exists(mlwp): return {"facade": "nomlw"}
    ml = open(mlwp).read().split("\n")
    meth = qual.split("#")[0].split(".")[-1]
    cands = [i for i, x in enumerate(ml) if re.match(r"^  (let|with)\s+(rec\s+)?(ghost\s+)?(function\s+)?\w*%s\b" % re.escape(meth), x)]
    if not cands: return {"facade": "noblock"}
    s = cands[0]
    s, e = mlw_block(ml, s + 2)
    blk = "\n".join(ml[s:e])
    parts = blk.split("\n  =\n", 1)
    body = parts[1] if len(parts) > 1 else blk
    body_nohoist = "\n".join(x for x in body.split("\n") if not re.match(r"\s*let \w+ = ref .* in\s*$", x))
    used = [p for p in params if p != "self" and re.search(r"\b%s\b" % re.escape(p), body_nohoist)]
    uses_self = "self" in params and re.search(r"\bself\b", body_nohoist) is not None
    marks = {k: len(re.findall(p, body)) for k, p in [("anyval", r"\bany (int|\(array int\)|bool|string)"),
                                                      ("zeroary", r"\(\w+ \(\)\)"), ("getattr", r"getattr"),
                                                      ("hash", r"[^\w.]\d{6,}\b")] if re.findall(p, body)}
    real_params = [p for p in params if p != "self"]
    blind = (not used) and not (uses_self and reads_self)
    if not real_params and not ("self" in params and reads_self):
        blind = None  # nothing to be blind to
    return {"facade": ("FACADE" if blind else ("n/a-noinputs" if blind is None else "reads-inputs")),
            "params_used": used, "nparams": len(real_params), "marks": marks, "blk_lines": e - s}

# ------------------------------------------------------------------ main loop


class _Abort(Exception): pass


import signal
def _onterm(sig, frm): raise _Abort()
signal.signal(signal.SIGTERM, _onterm)


trusted_quals = {}
for f, q, r in rows: trusted_quals.setdefault(f, set()).add(q)
resf = open(RES, "a")
for rel, qual, reason in rows:
    if (rel, qual) in done: continue
    if ONLY and f"{rel}::{qual}" not in ONLY: continue
    if time.time() - T0 > BUDGET: print("BUDGET", flush=True); break
    rec = {"file": rel, "qual": qual, "reason": reason}
    st, why = precheck(rel, qual, reason, trusted_quals)
    if st:
        rec.update(status=st, why=why); resf.write(json.dumps(rec) + "\n"); resf.flush(); print(st, rel, qual, flush=True); continue
    path = os.path.join(tree, "src/self-annotate/src", rel)
    orig = open(path).read()
    chain = []; emits = 0; row_t0 = time.time(); aborted = False; purged = set()
    try:
        pr = port(rel, qual)
        if pr != "ok":
            rec.update(status="SKIP-NOPORT", why=pr); continue
        lsrc = open(os.path.join(tree, "src/pycsl", rel)).read()
        lfn, _ = pick(ast.parse(lsrc), qual)
        mfn0, _ = pick(ast.parse(orig), qual)
        ret_ph = ann_placeholder(lfn.returns)
        if ret_ph is None:
            # mirror facade return value
            rs = [x for x in body_wo_doc(mfn0) if isinstance(x, ast.Return) and x.value is not None]
            ret_ph = ast.unparse(rs[0].value) if rs else "None"
        rec["nstmts"] = len(all_stmts(lfn))
        status = None
        while True:
            if emits >= MAXEMITS: status = "CAP-EMITS"; break
            if time.time() - T0 > BUDGET + 85:
                if row_t0 - T0 < 5:
                    status = "CAP-TIME"; break
                raise _Abort()
            aout, amap = emit_anchored(rel, qual, path); emits += 1
            pa = parse_out(aout) if aout is not None else {"ok": True}
            if pa["ok"]:
                out = emit("src/self-annotate/src/" + rel); emits += 1
                p = parse_out(out); pa = None
            else:
                p = pa
            if p["ok"]:
                status = "TCOK0" if not chain else "TCOK"
                rec["facade"] = facade_check(rel, qual, lfn)
                break
            if len(chain) >= MAXROUNDS: status = "CAP-ROUNDS"; rec["next"] = p.get("msg", "")[:300]; break
            ent = {"kind": p["kind"], "msg": p.get("msg", "")[:400]}
            stmt_ln = None; info = None; hint = None
            if p["kind"] == "why3":
                ml = open(p["mlw"]).read().split("\n")
                s, e = mlw_block(ml, p["line"])
                ent["block"] = block_name(ml[s])
                ent["errline"] = ml[p["line"] - 1].strip()[:200]
                ent["snip"] = ml[p["line"] - 1][p["c0"]:p["c1"]][:160]
                if pa is not None:
                    stmt_ln, info = locate_from(pa, amap, None)
                else:
                    stmt_ln, info = locate_why3(rel, qual, path, p); emits += 1
                ent.update({k: v for k, v in (info or {}).items() if k != "decls"})
            else:
                fn, _ = pick(ast.parse(open(path).read()), qual)
                hint, how = locate_fe(path, qual, p["msg"])
                ent["loc"] = how
                if hint is not None and isinstance(hint, ast.stmt): stmt_ln = hint.lineno
                elif hint is not None: stmt_ln = hint.lineno
            if stmt_ln is None and hint is None:
                ent["stmt"] = None
                chain.append(ent); status = "STUCK-LOCATE"; break
            src_now = open(path).read()
            fnn, _ = pick(ast.parse(src_now), qual)
            # statement text for classification
            tgt = None
            for pp, s in all_stmts(fnn):
                if s.lineno == stmt_ln and (tgt is None or (s.end_lineno - s.lineno) < (tgt.end_lineno - tgt.lineno)): tgt = s
            if tgt is None and isinstance(hint, ast.AST):
                for x in ast.walk(fnn):
                    if isinstance(x, type(hint)) and getattr(x, "lineno", -1) == hint.lineno: tgt = x; break
            if tgt is not None:
                if isinstance(tgt, (ast.If, ast.While)): ent["stmt"] = ("HDR " + type(tgt).__name__ + " " + ast.unparse(tgt.test))[:240]
                elif isinstance(tgt, ast.For): ent["stmt"] = ("HDR For " + ast.unparse(tgt.target) + " in " + ast.unparse(tgt.iter))[:240]
                elif isinstance(tgt, ast.With): ent["stmt"] = ("HDR With " + ", ".join(ast.unparse(i) for i in tgt.items))[:240]
                elif isinstance(tgt, ast.ExceptHandler): ent["stmt"] = ("HDR except " + (ast.unparse(tgt.type) if tgt.type else "") + (" as " + tgt.name if tgt.name else ""))[:240]
                elif isinstance(tgt, (ast.FunctionDef, ast.AsyncFunctionDef)): ent["stmt"] = "NESTED def " + tgt.name
                else: ent["stmt"] = ast.unparse(tgt)[:240]
                ent["stmt_line_rel"] = tgt.lineno - fnn.lineno
            if FIRST:
                chain.append(ent); status = "FIRST"; break
            act = None
            cur_lines = open(path).read().split("\n")
            phv = None
            if tgt is not None and "# NEUTRALISED" in "\n".join(cur_lines[tgt.lineno - 1:getattr(tgt, "end_lineno", tgt.lineno)]) and not isinstance(tgt, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                tg = [t.id for t in (tgt.targets if isinstance(tgt, ast.Assign) else [getattr(tgt, "target", None)]) if isinstance(t, ast.Name)] if isinstance(tgt, (ast.Assign, ast.AnnAssign)) else []
                phv = tg[0] if tg else "?"
            if phv is None and p["kind"] == "why3" and ent.get("anc") == "decl-area" and re.match(r"let (\w+) = ref", ent.get("errline", "")):
                vn = re.match(r"let (\w+) = ref", ent["errline"]).group(1)
                vn = re.sub(r"_len$", "", vn) if not re.search(r"\b%s\b[^\n]*# NEUTRALISED" % re.escape(vn), "\n".join(cur_lines)) else vn
                if re.search(r"\b%s\b[^\n]*# NEUTRALISED" % re.escape(vn), "\n".join(cur_lines)):
                    phv = vn
            if phv is None and p["kind"] == "why3" and ent.get("snip"):
                act = root_var_rewrite(path, qual, ent, p["msg"])
                if act == "PH-CONFLICT":
                    mm = re.fullmatch(r"\(?!?(\w+)\)?", ent["snip"].strip()); phv = mm.group(1) if mm else "?"; act = None
            if phv is not None:
                ent["ph"] = True
                if PURGE and phv != "?" and phv not in purged and len(purged) < 4:
                    purged.add(phv)
                    act = purge_var(path, qual, phv, ret_ph)
                    if act is None:
                        chain.append(ent); status = "STUCK-PH"; break
                    ent["act"] = act; chain.append(ent); continue
                chain.append(ent); status = "STUCK-PH"; break
            if act is None and p["kind"] == "fe" and ent.get("loc") == "call":
                act = mut_expr_rewrite(path, qual, p["msg"])
            if act is None:
              act = neutralise(path, qual, stmt_ln, info, ret_ph, kind_hint=tgt if tgt is not None and not isinstance(tgt, ast.stmt) else None)
            ent["act"] = act
            chain.append(ent)
            if act is None: status = "STUCK-NEUTRALISE"; break
            # repeated identical neutralisation guard
            if len(chain) >= 2 and chain[-1].get("stmt") == chain[-2].get("stmt") and chain[-1].get("msg") == chain[-2].get("msg") and chain[-1].get("stmt_line_rel") == chain[-2].get("stmt_line_rel"):
                status = "STUCK-REPEAT"; break
        rec.update(status=status, chain=chain, emits=emits)
        if status in ("TCOK", "TCOK0"):
            pass
    except _Abort:
        aborted = True
    except subprocess.TimeoutExpired:
        rec.update(status="TIMEOUT", chain=chain, emits=emits)
    except Exception as e:
        import traceback
        rec.update(status="CRASH", why=f"{type(e).__name__}: {e}", tb=traceback.format_exc()[-600:], chain=chain, emits=emits)
    finally:
        open(path, "w").write(orig)
        mlwp = path[:-3] + ".mlw"
        if os.path.exists(mlwp): os.remove(mlwp)
        if not aborted:
            resf.write(json.dumps(rec) + "\n"); resf.flush()
        print(rec.get("status") if not aborted else "ABORTED(redo)", rel, qual, len(chain), f"{time.time()-T0:.0f}s", flush=True)
    if aborted: break
