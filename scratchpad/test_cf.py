import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
from module6_whyml.generic_fold import recognize_final_pair, recognize_check_final, emit_check_final_group
from module6_whyml.identifiers import whyml_ident
src = open("src/self-annotate/src/core_ir_semantic.py").read()
ing = Module1_Ingestor(src); ed = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ed, pm); ua = w.process()
ua = splice_constant_exec(ua)
ir = json.loads(Module5_IREmitter(ua).generate_json())
funcs = ir.get("functions", [])
pair = recognize_final_pair(funcs)
print("pair walk:", pair["walk_name"] if pair else None)
cf_fn = next(f for f in funcs if f.get("name")=="_check_final")
desc = recognize_check_final(cf_fn, pair["walk_name"])
print("CF DESC:", json.dumps(desc, indent=1) if desc else "None")
if desc:
    print("=== EMIT ===")
    print("\n".join(emit_check_final_group(desc, whyml_ident)))
