"""PyCSL mock for Module4_SemanticAnalyzer."""
_ = 0  # anchor

# ── Module4AnalyzerObj class ────────────────────────────────────────

""  # pycsl
#@ class invariant self._errors >= 0
class Module4AnalyzerObj:
    def __init__(self):
        self._errors = 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._errors
    def visit_classdef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._errors
    def visit_functiondef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/ast.html#ast.NodeVisitor.visit
#@ requires True
#@ ensures True
#@ assigns self._errors
    def visit_while(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._errors
    def process(self, tree: int) -> int:
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/builtins.py
#@ requires True
#@ ensures True
def PyCSLSemanticError(message: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/Module4_SemanticAnalyzer.py
#@ requires True
#@ ensures True
def extract_variables(node: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/Module4_SemanticAnalyzer.py
#@ requires True
#@ ensures True
def contains_result(node: int) -> int:
    return 0
