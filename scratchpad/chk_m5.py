import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
from module6_whyml.generic_fold import recognize_global_call_target
src = open("src/self-annotate/src/frontend/Module5_IREmitter.py").read()
ing = Module1_Ingestor(src); ed = ing.process()
w = Module3_Weaver(src, ed, Module2_Parser()); ua = w.process()
ua = splice_constant_exec(ua)
ir = json.loads(Module5_IREmitter(ua).generate_json())
for f in ir.get("functions", []):
    if f.get("name","").endswith("_global_call_target"):
        print("name:", f.get("name"), "trusted:", f.get("trusted"), "recog:", recognize_global_call_target(f) is not None)
