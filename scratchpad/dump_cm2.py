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
for f in ir["functions"]:
    if f["name"]=="irscanner___collect_mutations":
        print("pann:", json.dumps(f.get("param_annotations")))
        print("formal_params:", f.get("formal_params"))
        print("ret:", f.get("return_annotation"))
        print(json.dumps(f.get("body"), indent=1))
print("==== TYPE DECLS str_set_constants ====")
for td in ir.get("type_decls",[]):
    if td.get("str_set_constants"):
        print(td.get("name"), "->", td.get("str_set_constants"))
