import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
src = open("src/self-annotate/src/Module6_WhyMLTranspiler.py").read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ex, pm); ua = w.process()
ua = splice_constant_exec(ua)
em = Module5_IREmitter(ua); ir = json.loads(em.generate_json())
for f in ir["functions"]:
    if "verify_module_groups" in f["name"]:
        print(f["name"], "ret=", f.get("return_annotation"), "params=", f.get("formal_params"))
        print(json.dumps(f.get("body"), indent=1))
print("---selftype---")
for f in ir["functions"]:
    if "verify_module_groups" in f["name"]:
        print("self_type=", repr(f.get("self_type")), "keys=", [k for k in f.keys()])
