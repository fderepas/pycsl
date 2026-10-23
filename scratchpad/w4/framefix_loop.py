"""framefix_loop.py <mirror.py-relpath> [max_iters]

The relaunch-#19 device, reused: drive `#@ assigns` to a FIXPOINT against Why3's OWN error
text, as a LOOP rather than an analysis.

Each iteration emits the mirror, reads the first frame error, maps the reported .mlw line
back to its enclosing `let <whyml-name>`, maps that to the mirror method, and merges the
protocol-stub field set into that method's `#@ assigns`. Repeats until L3-tc is green.
Handles both directions Why3 rejects:
  * "this expression produces an unlisted write effect"  -> the caller must declare more
  * "this write effect does not happen in the expression" -> the caller declares too much
"""
import ast, os, re, subprocess, sys

FIELDS = ["self._comp_content_counter","self._current_params","self._current_self_type",
          "self._frame_trigger_active","self._func_return_type","self._in_spec",
          "self._last_hval_get_raw","self._last_hval_get_str","self._needs_array_init",
          "self._obj_state_written","self._string_local_vars","self._todict_arg_wants_pymap",
          "self._uses_build_param_list_cache","self._uses_compute_return_type_cache",
          "self._uses_const_reflect_cache","self._uses_pyast_parser_cache",
          "self._uses_refine_tuple_return_type_cache"]
MARK = re.compile(r"^#@\s*\\trusted\b")
rel = sys.argv[1]
MAXIT = int(sys.argv[2]) if len(sys.argv) > 2 else 60
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


def mirror_method(whyml_name):
    """(class, method) for an emitted `<cls>__<meth>` / bare `<meth>` name."""
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


def merge(cls, name, add=True):
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
    new = sorted(set(cur) | set(FIELDS)) if add else sorted(set(cur) - set(FIELDS))
    if set(new) == set(cur):
        return False
    line = ind + "#@ assigns " + (", ".join(new) if new else "\\nothing")
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
    m = re.search(r'File "[^"]*", line (\d+),.*\n(.*)', out)
    msg = ""
    ln = None
    for mm in re.finditer(r'File "[^"]*", line (\d+), characters [^\n]*\n([^\n]*)', out):
        if "write effect" in mm.group(2):
            ln, msg = int(mm.group(1)), mm.group(2).strip()
            break
    if ln is None:
        print("STOP: not a frame error ->", out.strip().split("\n")[-1][:200])
        sys.exit(1)
    wn = enclosing(ln)
    tgt = mirror_method(wn) if wn else None
    if tgt is None:
        print(f"STOP: cannot map emitted symbol {wn!r} at line {ln}")
        sys.exit(1)
    add = "unlisted write effect" in msg
    ok = merge(tgt[0], tgt[1], add=add)
    print(f"  it{it}: {'+' if add else '-'} {tgt[0]}.{tgt[1]}  ({msg[:60]})" + ("" if ok else "  [NO CHANGE -> STOP]"))
    if not ok:
        sys.exit(1)
print("STOP: iteration cap")
sys.exit(1)
