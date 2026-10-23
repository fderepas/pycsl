import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
from module6_whyml.generic_fold import recognize_final_pair, emit_final_pair_group
from module6_whyml.identifiers import whyml_ident

src = open("src/self-annotate/src/core_ir_semantic.py").read()
ing = Module1_Ingestor(src); ed = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ed, pm); ua = w.process()
ua = splice_constant_exec(ua)
ir = json.loads(Module5_IREmitter(ua).generate_json())
funcs = ir.get("functions", [])
desc = recognize_final_pair(funcs)
print("DESC:", json.dumps(desc, indent=1, default=list) if desc else "None")
if desc:
    print("=== EMIT ===")
    for line in emit_final_pair_group(desc, whyml_ident):
        print(line)
