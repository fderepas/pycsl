import sys
sys.path.insert(0, "src/pycsl")
sys.path.insert(0, "src/pycsl/frontend")
from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser
from frontend.Module3_Weaver import Module3_Weaver
from frontend.Module5_IREmitter import Module5_IREmitter
import json
src = open("src/self-annotate/src/module6_whyml/stmt_control_flow.py").read()
ing = Module1_Ingestor(src); mods = ing.process()
# just parse the one method's for-loop; simpler: find via ast on the file
import ast
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_union_ctor_for_arm_tag":
        for s in ast.walk(node):
            if isinstance(s, ast.For):
                print("ITER:", ast.dump(s.iter))
