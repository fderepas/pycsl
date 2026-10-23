import sys, ast, inspect
sys.path.insert(0, "src/pycsl")
from frontend.Module5_IREmitter import PyCSLToJSONEmitter
print("method file:", inspect.getsourcefile(PyCSLToJSONEmitter._collect_class_str_set_constants))
lines,ln = inspect.getsourcelines(PyCSLToJSONEmitter._collect_class_str_set_constants)
print("first line no:", ln)
print("".join(lines[:6]))
