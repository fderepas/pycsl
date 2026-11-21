"""#32 spike: give EVERY `\trusted` mirror stub that declares `#@ assigns \nothing` (or
declares no `assigns` at all) its HONEST frame, derived from the LIVE transitive self-write
closure that bin/check-trusted-frame-honesty.py computes. Reports what it changed."""
import ast, importlib.util, os, re, sys

ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location(
    "fh", os.path.join(ROOT, "bin", "check-trusted-frame-honesty.py"))
fh = importlib.util.module_from_spec(spec)
sys.argv = ["fh"]
spec.loader.exec_module(fh)
classes, bases, funcs, tables = fh._parse_tree(fh.LIVE_ROOT)
direct, trans = fh._self_write_fixpoint(classes, bases, funcs, tables)

MARK = re.compile(r"^#@\s*\\trusted\b")
changed = []
for dp, dn, fn in os.walk(fh.MIRROR_ROOT):
    for f in sorted(fn):
        if not f.endswith(".py"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, fh.MIRROR_ROOT)
        src = open(p).read()
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        edits = []          # (assigns_line_idx or None, insert_at, text)

        def walk(scope, cls):
            for n in scope:
                if isinstance(n, ast.ClassDef):
                    walk(n.body, n.name)
                    continue
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                first = min([d.lineno for d in n.decorator_list] + [n.lineno]) - 1
                i, b0 = first - 1, first
                while i >= 0:
                    st = lines[i].strip()
                    if not (st.startswith("#") or st.startswith("@") or st == ""):
                        break
                    b0 = i
                    i -= 1
                blk = [lines[k].strip() for k in range(b0, first)]
                if not any(MARK.match(x) for x in blk):
                    continue
                ai = next((k for k in range(b0, first)
                           if lines[k].strip().startswith("#@ assigns")), None)
                cur = []
                if ai is not None:
                    txt = lines[ai].strip()[len("#@ assigns"):].strip()
                    if txt and txt != "\\nothing":
                        cur = [x.strip() for x in txt.split(",") if x.strip()]
                if cur:
                    return_ = None      # already names something: leave it (only widen below)
                ws = set()
                for key, v in trans.items():
                    if key[-1] == n.name and (cls is None or cls in key):
                        ws |= v
                if not ws:
                    continue
                want = sorted(set(cur) | {"self." + w for w in ws})
                if set(want) == set(cur):
                    continue
                ind = lines[first][:len(lines[first]) - len(lines[first].lstrip())]
                edits.append((ai, first, ind + "#@ assigns " + ", ".join(want),
                              (cls + "." if cls else "") + n.name))

        walk(tree.body, None)
        if not edits:
            continue
        for ai, first, text, name in sorted(edits, key=lambda e: -(e[1])):
            if ai is not None:
                lines[ai] = text
            else:
                lines.insert(first, text)
            changed.append((rel, name))
        open(p, "w").write("\n".join(lines))
print("stubs given an honest frame:", len(changed))
for c in changed[:200]:
    print("   ", c[0], c[1])
