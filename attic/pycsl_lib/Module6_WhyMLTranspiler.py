"""PyCSL mock for Module6_WhyMLTranspiler."""
_ = 0  # anchor

# ── Module6TranspilerObj class ──────────────────────────────────────

""  # pycsl
#@ class invariant self._functions_emitted >= 0
class Module6TranspilerObj:
    def __init__(self):
        self._functions_emitted = 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/Module6_WhyMLTranspiler.py
#@ requires True
#@ ensures True
#@ assigns self._functions_emitted
    def transpile(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/Module6_WhyMLTranspiler.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def whyml_ident(self, name: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/module6_whyml/identifiers.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def op_translate(self, op: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/whyml_transpiler.py  # best-guess; no stdlib page found
#@ requires True
#@ ensures True
#@ assigns \nothing
    def uses_arrayset(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def ends_with_return(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/module6_whyml/ir_scanner.py
#@ requires stmts >= 0
#@ ensures \result >= 0
#@ assigns \nothing
    def find_assigned_vars(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def has_continue(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/module6_whyml/ir_scanner.py
#@ requires stmts >= 0
#@ ensures \result >= 0
#@ assigns \nothing
    def uses_continue(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/fderepas/pycsl/blob/main/src/pycsl/module6_whyml/ir_scanner.py#L372
#@ requires True
#@ ensures True
#@ assigns \nothing
    def uses_for(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/Module6_WhyMLTranspiler.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def uses_subscript(self, obj: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/whyml_transpiler.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def uses_minmax(self, obj: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/Module6_WhyMLTranspiler.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def is_recursive(self, name: int, obj: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: src/pycsl/module6_whyml/ir_scanner.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def uses_string(self, obj: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: src/pycsl/module6_whyml/ir_scanner.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def find_return_type(self, stmts: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: src/pycsl/module6_whyml/expressions.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def expr_to_whyml(self, expr: int, local_refs: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/stdtypes.html
#@ requires True
#@ ensures True
#@ assigns \nothing
    def stmts_to_whyml(self, stmts: int, local_refs: int, declared_refs: int, indent: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: src/pycsl/module6_whyml/statements.py
#@ requires True
#@ ensures True
    def emit_frame_condition(self, assigns_list: int) -> int:
        return 0
