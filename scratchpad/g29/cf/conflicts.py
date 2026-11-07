"""Census of `_add_abstract_op` same-name/same-arity conflicts (route #166).

Usage: python3 conflicts.py <repo-root> <out.tsv> <file>...
Runs the pycsl pipeline in-process per file with the op registry patched to record every
conflict (name, existing decl, new decl), emission only."""
import sys, os, io, contextlib, runpy
root, out = sys.argv[1], sys.argv[2]
files = sys.argv[3:]
sys.path.insert(0, os.path.join(root, "src", "pycsl"))
import module6_whyml.abstract_ops as ao
_orig = ao.AbstractOpsMixin._add_abstract_op if hasattr(ao, "AbstractOpsMixin") else None
cls = None
for v in vars(ao).values():
    if isinstance(v, type) and "_add_abstract_op" in vars(v):
        cls = v
        break
orig = cls._add_abstract_op
CUR = {"f": ""}
rows = []
def patched(self, decl):
    parts = decl.split()
    name = None
    if len(parts) >= 2 and parts[0] == "val":
        name = parts[2] if parts[1] in ("constant", "function") and len(parts) > 2 else parts[1]
    if name and name in self._abstract_ops and self._abstract_ops[name] != decl:
        if cls._decl_arity(self._abstract_ops[name]) == cls._decl_arity(decl):
            rows.append((CUR["f"], name, self._abstract_ops[name].replace("\n", " "), decl.replace("\n", " ")))
    return orig(self, decl)
cls._add_abstract_op = patched
import pycsl as P
for f in files:
    CUR["f"] = f
    flags = []
    try:
        with open(f) as fh:
            for line in fh:
                if line.startswith("# pycsl-flags:"):
                    flags = line.split(":", 1)[1].split()
                    break
    except Exception:
        pass
    argv = ["pycsl.py", "--no-proof", "--no-typecheck"] + flags + [f]
    if "src/self-annotate" in f:
        argv += ["--import-path", os.path.join(root, "src", "pycsl")]
    old = sys.argv
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                P.main()
            except SystemExit:
                pass
            except Exception:
                pass
    finally:
        sys.argv = old
with open(out, "w") as fh:
    for r in rows:
        fh.write("\t".join(r) + "\n")
print("conflicts:", len(rows))
