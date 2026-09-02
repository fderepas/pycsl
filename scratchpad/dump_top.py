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
print("TOP-LEVEL KEYS:", list(ir.keys()))
for k in ("module_globals","module_constants","constants","class_constants"):
    if k in ir:
        print(f"--- {k} ---")
        print(json.dumps(ir[k], indent=1)[:2000])
