import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ex, pm); ua = w.process()
ua = splice_constant_exec(ua)
em = Module5_IREmitter(ua); ir = json.loads(em.generate_json())
print("FUNCTIONS:", [f.get("name") for f in ir["functions"]])
print("TRUSTED:", [f.get("name") for f in ir.get("trusted_funcs",[])][:40])
print("TYPE_DECLS keys:")
for td in ir.get("type_decls",[]):
    print("  ", td.get("name"), "| str_set_constants:", td.get("str_set_constants"))
