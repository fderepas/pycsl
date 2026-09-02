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
print("top keys:", list(ir.keys()))
def find(node, name, path=""):
    if isinstance(node, dict):
        if node.get("name")==name and "formal_params" in node:
            print("FOUND at", path)
            print("pann:", json.dumps(node.get("param_annotations")))
            print("ret:", node.get("return_annotation"))
            print(json.dumps(node.get("body"), indent=1))
            return True
        for k,v in node.items():
            if find(v, name, path+"/"+str(k)): return True
    elif isinstance(node, list):
        for i,x in enumerate(node):
            if find(x, name, path+f"[{i}]"): return True
    return False
find(ir, "_collect_mutations")
# also dump str_set_constants presence
def find_types(node):
    if isinstance(node, dict):
        if "str_set_constants" in node:
            print("STR_SET_CONSTANTS:", json.dumps(node["str_set_constants"]))
        for v in node.values(): find_types(v)
    elif isinstance(node, list):
        for x in node: find_types(x)
find_types(ir)
