import sys, json
sys.path.insert(0, "src/pycsl")
from Module1_Ingestor import Ingestor
from Module2_Parser import Parser
from Module3_Weaver import Weaver
from Module4_SemanticAnalyzer import SemanticAnalyzer
from Module5_IREmitter import IREmitter
src = open("src/self-annotate/src/module6_whyml/scc.py").read()
mod = Ingestor().ingest_string(src, "scc.py")
p = Parser().parse(mod)
w = Weaver().weave(p, mod)
sa = SemanticAnalyzer(); sa.analyze(w)
emit = IREmitter()
ir = emit.emit(w)
for f in ir.get("functions", []):
    if f.get("name","").endswith("find_self_method_calls"):
        print("NAME", f["name"])
        print("PARAMS", f.get("formal_params"))
        print("PANN", json.dumps(f.get("param_annotations")))
        print("RET", f.get("return_annotation"))
        print("BODYLEN", len(f.get("body", [])))
        print(json.dumps(f.get("body"), indent=1)[:6000])
        break
