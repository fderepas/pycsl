#!/usr/bin/env python3
"""frame_witness.py <tree> <prog.py> [--no-proof] : RUNTIME witness for the Gate-S refutation.
Wraps every `_handle_*` method of the LIVE GhostCollectionOpsMixin / GhostSpecOpsMixin (whose mirror
copies are VERIFIED with `#@ assigns \\nothing`) and records, per call, which `self.<f>` attributes
changed value (repr fingerprint before vs after). Then runs the live pycsl pipeline (--no-proof) on prog."""
import sys, os, runpy, hashlib
T, PROG = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(T, "src/pycsl"))
import module6_whyml.expr_ghost_collections as gc, module6_whyml.expr_ghost_spec_ops as gs
def fp(o):
    out = {}
    for k, v in vars(o).items():
        try: r = repr(v)
        except Exception: r = "<unrepr>"
        out[k] = hashlib.sha1(r.encode()).hexdigest()
    return out
HITS = {}
CALLS = {}
def wrap(cls, name):
    f = getattr(cls, name)
    def w(self, *a, **k):
        b = fp(self); r = f(self, *a, **k); af = fp(self)
        ch = sorted(x for x in set(b) | set(af) if b.get(x) != af.get(x))
        CALLS[cls.__name__ + "." + name] = CALLS.get(cls.__name__ + "." + name, 0) + 1
        if ch: HITS.setdefault(cls.__name__ + "." + name, set()).update(ch)
        return r
    setattr(cls, name, w)
for cls in (gc.GhostCollectionOpsMixin, gs.GhostSpecOpsMixin):
    for n in list(vars(cls)):
        if n.startswith("_handle_"): wrap(cls, n)
sys.argv = [os.path.join(T, "src/pycsl/pycsl.py"), PROG, "--import-path", os.path.join(T, "src/pycsl"), "--no-proof"]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit as e:
    print("pycsl exit", e.code)
finally:
    print("WITNESS_CALLS", sorted(CALLS.items()))
    for k, v in sorted(HITS.items()): print("WITNESS_WRITE", k, "->", sorted(v))
    print("WITNESS_DONE hits=%d" % len(HITS))
