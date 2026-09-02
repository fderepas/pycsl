import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
f = "src/self-annotate/src/frontend/Module3_Weaver.py"
src = open(f).read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser()
uast = splice_constant_exec(Module3_Weaver(src, ex, pm).process())
ir = json.loads(Module5_IREmitter(uast).generate_json())
def find(fns, name):
    for fn in fns:
        if fn.get("name")==name: return fn
    return None
# methods live under classes
allf = list(ir.get("functions", []))
for c in ir.get("classes", []):
    allf += c.get("methods", [])
fn = find(allf, "_is_trivial_new")
print(json.dumps(fn, indent=1) if fn else "NOT FOUND; classes methods:")
if not fn:
    for c in ir.get("classes", []):
        print(c.get("name"), [m.get("name") for m in c.get("methods",[])][:5])
