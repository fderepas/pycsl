"""PyCSL mock for Module6_WhyMLTranspiler."""
_ = 0  # anchor

# ── Module6TranspilerObj class ──────────────────────────────────────

""  # pycsl
#@ class invariant self._functions_emitted >= 0
class Module6TranspilerObj:
    def __init__(self):
        self._functions_emitted = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns self._functions_emitted
    def transpile(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def whyml_ident(self, name: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def op_translate(self, op: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_arrayset(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def ends_with_return(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def find_assigned_vars(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def has_continue(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_continue(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_for(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_subscript(self, obj: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_minmax(self, obj: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def is_recursive(self, name: int, obj: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def uses_string(self, obj: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def find_return_type(self, stmts: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def expr_to_whyml(self, expr: int, local_refs: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def stmts_to_whyml(self, stmts: int, local_refs: int, declared_refs: int, indent: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit_frame_condition(self, assigns_list: int) -> int:
        return 0
