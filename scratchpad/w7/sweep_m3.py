import sys, os, importlib
sys.path.insert(0, "src/pycsl")
M1 = importlib.import_module('frontend.Module1_Ingestor')
M3 = importlib.import_module('frontend.Module3_Weaver')
P  = importlib.import_module('frontend.Module2_Parser')
bad = 0
for root in ["test-suite/corpus", "src/self-annotate", "src/pycsl_lib", "src/pycsl", "tests"]:
    for dirpath, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "attic")]
        for fn in sorted(fns):
            if not fn.endswith(".py"): continue
            p = os.path.join(dirpath, fn)
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
                data = M1.Module1_Ingestor(src).process()
            except Exception:
                continue
            w = M3.Module3_Weaver(src, data, P.Module2_Parser())
            try:
                w._reject_misplaced_directives()
            except Exception as e:
                bad += 1
                print("%-70s %s" % (p, str(e).split(" — ")[0]))
print("TOTAL offending files:", bad)
