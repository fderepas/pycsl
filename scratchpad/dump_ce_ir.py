import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter

f = "src/self-annotate/src/frontend/exec_splice.py"
src = open(f).read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser()
w = Module3_Weaver(src, ex, pm)
uast = w.process()
uast = splice_constant_exec(uast)
em = Module5_IREmitter(uast)
ir = json.loads(em.generate_json())
for fn in ir.get("functions", []):
    if fn.get("name") in ("_contains_exec","_is_constant_exec"):
        print("=====", fn.get("name"))
        print(json.dumps(fn, indent=1))
