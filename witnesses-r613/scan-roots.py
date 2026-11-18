"""route #613 step 3: which local entries named like a module the import closure may reach exist in
each resolution root of each tree (corpus root, pyref, mirror). Static scan (no pycsl import):
roots per file = realpath dir, dir, cwd (= tree root), src/, src/pycsl/Lib, each --import-path.
Usage: python3 -I scan-roots.py <tree-root>"""
import ast, os, sys, sysconfig, shlex

T = os.path.abspath(sys.argv[1])
std = sysconfig.get_paths()["stdlib"]
names = set(sys.stdlib_module_names) | set(sys.builtin_module_names)
for dp, dn, fn in os.walk(std):
    dn[:] = sorted(d for d in dn if d not in ("__pycache__", "site-packages", "dist-packages"))
    for f in fn:
        if f.endswith(".py"):
            try:
                tr = ast.parse(open(os.path.join(dp, f), "rb").read())
            except Exception:
                continue
            for n in ast.walk(tr):
                if isinstance(n, ast.Import):
                    names |= {a.name.split(".")[0] for a in n.names}
                elif isinstance(n, ast.ImportFrom) and not n.level and n.module:
                    names.add(n.module.split(".")[0])
names.discard("__main__")


def files(kind):
    if kind == "root":
        d = os.path.join(T, "test-suite/corpus/pycsl-reference")
        return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".py"))
    if kind == "pyref":
        d = os.path.join(T, "test-suite/corpus/python-reference")
    else:
        d = os.path.join(T, "src/self-annotate/src")
    out = []
    for dp, dn, fn in os.walk(d):
        out += [os.path.join(dp, f) for f in fn if f.endswith(".py")]
    return sorted(out)


for kind in ("root", "pyref", "mirror"):
    rootent = {}
    nfiles = {}
    for f in files(kind):
        ip = []
        if kind == "mirror":
            ip = [os.path.join(T, "src/pycsl")]
        else:
            for line in open(f, errors="replace"):
                if line.startswith("# pycsl-flags:"):
                    a = shlex.split(line.split(":", 1)[1])
                    ip = [os.path.join(T, a[i + 1]) for i, x in enumerate(a)
                          if x == "--import-path" and i + 1 < len(a)]
                    break
        roots = []
        for r in [os.path.dirname(os.path.realpath(f)), os.path.dirname(os.path.abspath(f)), T,
                  os.path.join(T, "src"), os.path.join(T, "src/pycsl/Lib"), *ip]:
            if r not in roots and os.path.isdir(r):
                roots.append(r)
        hit = False
        for r in roots:
            if r not in rootent:
                rootent[r] = sorted(e for e in os.listdir(r) if e.split(".", 1)[0] in names)
            if rootent[r]:
                hit = True
                nfiles.setdefault(r, 0)
                nfiles[r] += 1
    print(f"== {kind}: {len(files(kind))} files")
    for r in sorted(nfiles):
        print(f"  root {os.path.relpath(r, T) or '.'}: {nfiles[r]} file(s) search it; entries: "
              + " ".join(rootent[r]))
