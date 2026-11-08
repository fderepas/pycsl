import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
path = "src/self-annotate/src/frontend/ir_inline.py"
src = open(path).read()
ing = Module1_Ingestor(src); ed = ing.process()
pm = Module2_Parser()
w = Module3_Weaver(src, ed, pm); ua = w.process()
ua = splice_constant_exec(ua)
em = Module5_IREmitter(ua)
ir = json.loads(em.generate_json())
for f in ir.get("functions", []):
    if f.get("name","").endswith("_method_edges"):
        print("params:", f.get("formal_params"))
        print("pann:", f.get("param_annotations"))
        print("ret:", f.get("return_annotation"))
        print(json.dumps(f.get("body"), indent=1))
