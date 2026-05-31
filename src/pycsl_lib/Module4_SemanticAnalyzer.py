"""PyCSL mock for Module4_SemanticAnalyzer."""
_ = 0  # anchor

# ── Module4AnalyzerObj class ────────────────────────────────────────

""  # pycsl
#@ class invariant self._errors >= 0
class Module4AnalyzerObj:
    def __init__(self):
        self._errors = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._errors
    def visit_classdef(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._errors
    def visit_functiondef(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._errors
    def visit_while(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._errors
    def process(self, tree: int) -> int:
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PyCSLSemanticError(message: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def extract_variables(node: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def contains_result(node: int) -> int:
    return 0
