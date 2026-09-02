import sys, json
sys.path.insert(0, "src/pycsl")
sys.argv = ["pycsl", "src/self-annotate/src/module6_whyml/auto_trust.py", "--import-path", "src/pycsl", "--no-proof"]
import importlib
# Monkeypatch to intercept the functions list at emit time
import module6_whyml.generic_fold as gf
orig = gf.recognize_build_method_writes_map
seen = {}
# Instead: hook recognize_collect_map_typed_locals_pairs which receives full functions list
orig_pairs = gf.recognize_collect_map_typed_locals_pairs
def hook(functions):
    names = [f.get("name") for f in functions if isinstance(f,dict)]
    idxs = [i for i,nm in enumerate(names) if nm and nm.endswith("_extract_array_lengths")]
    for i in idxs:
        print("=== OUTER idx", i, names[i])
        print("neighbors:", names[max(0,i-2):i+4])
        for j in range(i, min(len(functions), i+3)):
            f = functions[j]
            print("----", j, f.get("name"), "params=", f.get("formal_params"), "ret=", f.get("return_annotation"), "self_type=", f.get("self_type"))
            print("   BODY:", json.dumps(f.get("body"))[:1500])
    raise SystemExit(0)
gf.recognize_collect_map_typed_locals_pairs = hook
import runpy
try:
    runpy.run_path("src/pycsl/pycsl.py", run_name="__main__")
except SystemExit:
    pass
