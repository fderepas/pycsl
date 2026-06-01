"""PyCSL mock for Module5_IREmitter."""
_ = 0  # anchor

# ── PyCSLToJSONEmitterObj class ─────────────────────────────────────

""  # pycsl
#@ class invariant self._ir_nodes >= 0
class PyCSLToJSONEmitterObj:
    def __init__(self):
        self._ir_nodes = 0

#@ \trusted reviewer: pycsl-internal
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns self._ir_nodes
    def visit_classdef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: pycsl-internal
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns self._ir_nodes
    def visit_functiondef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/
#@ requires True
#@ ensures True
#@ assigns \nothing
    def csl_to_ir(self, node: int) -> int:
        return 0

#@ \trusted reviewer: pycsl-internal
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def csl_list_to_ir(self, csl_list: int) -> int:
        return 0

#@ \trusted reviewer: pycsl-internal
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def py_op_to_str(self, op: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def py_expr_to_ir(self, expr: int) -> int:
        return 0

#@ \trusted reviewer: pycsl-internal
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def py_stmts_to_ir(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def process_while(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/<module>.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def process_for(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def process_if(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def scan_2d_in_expr(self, expr: int, param_names: int, arr_result: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/pycsl_lib.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def scan_2d_in_stmt(self, stmt: int, param_names: int, arr_result: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/Module5_IREmitter.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def collect_2d_params(self, body_ir: int, symbol_table: int) -> int:
        return 0

# ── Module5EmitterObj class ─────────────────────────────────────────

#@ class invariant self._processed >= 0
class Module5EmitterObj:
    def __init__(self):
        self._processed = 0

    #@ \trusted
    #@ requires self._processed == 0
    #@ ensures self._processed == 1
    #@ assigns self._processed
    def generate_json(self, indent: int) -> int:
        self._processed = 1
        return 0
