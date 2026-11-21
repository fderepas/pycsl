import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
from module6_whyml.generic_fold import recognize_module_binding_names, emit_module_binding_names_group

def build(src):
    ing = Module1_Ingestor(src); ex = ing.process()
    pm = Module2_Parser(); w = Module3_Weaver(src, ex, pm); ua = w.process()
    ua = splice_constant_exec(ua)
    em = Module5_IREmitter(ua); ir = json.loads(em.generate_json())
    for f in ir.get("functions", []):
        if f.get("name","").endswith("_module_binding_names"):
            d = recognize_module_binding_names(f)
            return d, emit_module_binding_names_group(d, lambda s: s) if d else None
    return None, None

orig = open("src/self-annotate/src/module6_whyml/expressions.py").read()
d0, e0 = build(orig)
print("ORIG recognized:", d0 is not None, "keys:", d0)
mut = orig.replace('ir.get("functions", [])', 'ir.get("functionsMUT", [])')
assert mut != orig, "mutation did not apply"
d1, e1 = build(mut)
print("MUT recognized:", d1 is not None, "funcs_key:", (d1 or {}).get("funcs_key"))
line_orig = [l for l in (e0 or []) if "pget_list" in l and "ffold" in l]
line_mut  = [l for l in (e1 or []) if "pget_list" in l and "ffold" in l]
print("ORIG ffold line:", line_orig)
print("MUT  ffold line:", line_mut)
print("MUTATION-SENSITIVE:", line_orig != line_mut and any("functionsMUT" in l for l in line_mut))
