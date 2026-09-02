import sys, json
sys.path.insert(0, "src/pycsl")
sys.argv = ["pycsl", "src/self-annotate/src/frontend/Module5_IREmitter.py", "--emit-ir", "/tmp/x"]
# Instead, use the emitter API to get IR
import ast
from frontend.Module2_Parser import ContractWrapper
# Simpler: parse the classify source and print the return-tuple IR via Module5
