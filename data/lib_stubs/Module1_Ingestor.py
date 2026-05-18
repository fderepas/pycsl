"""PyCSL mock for Module1_Ingestor."""
_ = 0  # anchor

# ── PyCSLVisitorObj class ───────────────────────────────────────────

""  # pycsl
#@ class invariant self._contracts_found >= 0
class PyCSLVisitorObj:
    def __init__(self):
        self._contracts_found = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_module(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_classdef(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def leave_classdef(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_functiondef(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_while(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_for(self, node: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._contracts_found
    def visit_simple_statement(self, node: int) -> int:
        return 0

# ── Module1IngestorObj class ────────────────────────────────────────

#@ class invariant self._processed >= 0
class Module1IngestorObj:
    def __init__(self):
        self._processed = 0

    #@ \trusted
    #@ requires self._processed == 0
    #@ ensures self._processed == 1
    #@ assigns self._processed
    def process(self) -> int:
        self._processed = 1
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PyCSLContract(node_type: int, node_name: int, line_number: int, contracts: int) -> int:
    return 0
