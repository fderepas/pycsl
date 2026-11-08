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

def walk(fns):
    for f in fns:
        if f.get("name") == "_module_binding_names":
            print("FOUND name=", f["name"], "params=", f.get("formal_params"),
                  "ret=", f.get("return_annotation"), "self_type=", f.get("self_type"),
                  "kind=", f.get("kind"))
            print(json.dumps(f.get("body"), indent=1))
            print("PANN=", json.dumps(f.get("param_annotations")))

walk(ir.get("functions", []))
for c in ir.get("classes", []):
    walk(c.get("methods", []))
