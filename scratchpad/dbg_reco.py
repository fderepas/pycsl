import sys, json
sys.path.insert(0, "src/pycsl")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.exec_splice import splice_constant_exec
from frontend.Module5_IREmitter import Module5_IREmitter
from module6_whyml.generic_fold import recognize_collect_mutations, _recognize_collect_mutations
src = open("src/self-annotate/src/module6_whyml/ir_scanner.py").read()
ing = Module1_Ingestor(src); ex = ing.process()
pm = Module2_Parser(); w = Module3_Weaver(src, ex, pm); ua = w.process()
ua = splice_constant_exec(ua)
em = Module5_IREmitter(ua); ir = json.loads(em.generate_json())
css = ir.get("class_str_set_constants", {})
print("class_str_set_constants keys:", list(css.keys()))
print("IRScanner members:", css.get("IRScanner"))
f = [x for x in ir["functions"] if x["name"]=="irscanner___collect_mutations"][0]
print("contracts:", json.dumps(f.get("contracts")))
try:
    r = _recognize_collect_mutations(f, css)
    print("RECOGNIZED:", json.dumps(r, indent=1) if r else None)
except Exception as e:
    import traceback; traceback.print_exc()
