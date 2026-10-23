import sys, os, io, collections
sys.path.insert(0, "src/pycsl")
sys.argv = ["x"]
import importlib
M1 = importlib.import_module('frontend.Module1_Ingestor')

drops = collections.Counter()
detail = collections.defaultdict(list)
CUR = [""]

orig_emit = M1._Harvester._emit_target
def emit(self, tgt):
    contracts = []
    if (tgt.node_type in M1._HEADER_CONSUMERS and not self._header_consumed
            and self._module_header):
        contracts.extend(self._normalize_leading(self._module_header))
    contracts.extend(self._normalize_leading(tgt.leading))
    if contracts and tgt.node_type is None:
        drops["anchorless(if/try/match)"] += len(contracts)
        detail["anchorless(if/try/match)"].append("%s:%d %s" % (CUR[0], tgt.report_line, contracts))
    return orig_emit(self, tgt)
M1._Harvester._emit_target = emit

orig_assign = M1._Harvester._assign
def assign(self):
    for c in self._coms:
        if any(lo <= c.lineno < hi for lo, hi in self._dec_ranges):
            drops["decorator-whitespace"] += 1
            detail["decorator-whitespace"].append("%s:%d %s" % (CUR[0], c.lineno, c.text.strip()))
    return orig_assign(self)
M1._Harvester._assign = assign

roots = sys.argv[1:] if len(sys.argv) > 1 else None
import glob
ROOTS = ["test-suite/corpus", "src/self-annotate", "src/pycsl_lib", "src/pycsl"]
per_root = {}
for root in ROOTS:
    drops.clear(); detail.clear()
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "attic")]
        for fn in files:
            if not fn.endswith(".py"): continue
            p = os.path.join(dirpath, fn); CUR[0] = p
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
                M1.Module1_Ingestor(src).process()
            except Exception:
                pass
    print("== %s ==" % root)
    if not drops: print("   (none)")
    for k, v in drops.items():
        print("   %4d  %s" % (v, k))
        for d in detail[k][:6]:
            print("        %s" % d)
