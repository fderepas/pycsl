import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
src = open(sys.argv[1]).read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ex, pm); ua = w.process()
ua = splice_constant_exec(ua)
em = Module5_IREmitter(ua); ir = json.loads(em.generate_json())
print("TOPKEYS", list(ir.keys()))
print("NFUNCS", len(ir.get("functions", [])))
names=[f.get("name") for f in ir.get("functions",[])]
print("has_mbn_in_funcs", "_module_binding_names" in names)
print("classes", [c.get("name") for c in ir.get("classes",[])][:5], "...")
for c in ir.get("classes", []):
    ms=[m.get("name") for m in c.get("methods",[])]
    if "_module_binding_names" in ms:
        print("class", c.get("name"), "has mbn")
print("---NAMES with binding---")
for f in ir.get("functions",[]):
    if "binding" in f.get("name","") or "in_globals" in f.get("name",""):
        print(f.get("name"), "params=",f.get("formal_params"),"ret=",f.get("return_annotation"),"kind=",f.get("kind"),"self_type=",f.get("self_type"))
print("---TRUSTED---")
tf=ir.get("trusted_funcs")
print(type(tf), (list(tf)[:5] if hasattr(tf,'__iter__') else tf))
