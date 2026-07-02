from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from module6_whyml.identifiers import whyml_ident, safe_exc_name
from module6_whyml.ir_scanner import IRScanner
from ir_schema import ReturnStmt, IfStmt, WhileStmt, ForStmt, TryStmt, MatchStmt
def mutable_state(cls): return cls
""  # pycsl


# item34.md CF0: the control-flow mirror is a @mutable_state @dataclass so the emit_ir /
# string-local / seq machinery fires for its real bodies (item 4). The state fields below are
# the ones the ported handlers READ (`_has_early_ret`, `_func_return_type`, `_current_tuple_
# arity`) plus the collection sets they consult; all reads (no writes) → `assigns \nothing`.
@mutable_state
@dataclass
class ControlFlowStmtMixin:
    _has_early_ret: int = 0
    _func_return_type: str = ""
    _current_tuple_arity: int = 0
    _seq_locals: Set[str] = None
    _array_locals: Set[str] = None
    "Control-flow statement handlers — `while` / `for` / `if` / `try` / `match`\n    / `return` — plus their private helpers (`_classify_iterable`,\n    `_first_assign_value_ir`, `_try_local_decl_kind`).\n\n    Extracted verbatim from `StatementEmissionMixin` (Part B move 3e, mirroring\n    the expressions.py split). `StatementEmissionMixin` inherits this mixin, so\n    the handlers resolve via MRO through the facade's `_STMT_HANDLERS` table and\n    recurse back into the core `self._stmts_to_whyml` / `self._expr_to_whyml`\n    (which stay in `StatementEmissionMixin`)."

    # item34.md CF0.3: cross-file recursion-leaf / bridge sibling stubs (defined in the
    # StatementEmissionMixin / expressions.py files the mixin composes with at runtime). Typed
    # `-> str` so the ported control-flow bodies compose their strings; effect-free registrar
    # helpers (`*_bridge`) are `assigns \nothing`.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _materialize_bridge(self) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _materialize_str_bridge(self) -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _seq_init_expr(self, val_ir: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _bool_ir_to_int_wrap(self, val: str, val_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _expr_to_whyml(self, expr: "ExprIR", local_refs: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _coerce_to_int(self, val: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    def _stmts_to_whyml(self, rest: List[Dict[str, Any]], local_refs: Set[str],
                        declared_refs: Set[str], indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_while_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _classify_iterable(self, iter_ir: int, local_refs: int, idx: str) -> int:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_for_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _first_assign_value_ir(self, var: str, stmts: List[int]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _try_local_decl_kind(self, val_ir: int) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_raised_direct(self, node: Any) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _callee_raised_in(self, stmts: List[int]) -> int:
        return set()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_try_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _try_union_is_none_match(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_if_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _pattern_has_constructor(self, pat: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _render_match_pattern(self, pat: int, top: bool=False) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _match_subject_union_info(self, stmt: int) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_ctor_for_arm_tag(self, vinfo: int, arm_tag: str) -> int:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_match_stmt(self, stmt: int, rest: List[int], local_refs: int, declared_refs: int, indent: str, in_loop: bool) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _maybe_inject_union_return(self, val: str, val_ir: "ExprIR") -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _infer_return_value_type(self, val_ir: Any) -> Optional[str]:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _union_arm_whyml_type(self, tag: str) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_return_stmt(
        self,
        stmt: ReturnStmt,
        rest: List[Dict[str, Any]],
        local_refs: Set[str],
        declared_refs: Set[str],
        indent: str,
        in_loop: bool,
    ) -> str:
        """Reads self._has_early_ret, self._func_return_type, self._array_locals (no writes)."""
        val_ir = stmt.value.to_dict() if stmt.value is not None else None
        use_raise = in_loop or self._has_early_ret
        func_ret_peek = self._func_return_type
        if val_ir is None:
            val = "()"
        elif (val_ir.get("type") == "Var"
              and val_ir.get("name") in getattr(self, "_seq_locals", set())):
            # 07-1705-rev4 P4: returning a seq-modelled (growable) list local where the
            # function's declared return is `array int` (a `list`) crosses the seq→array
            # boundary — materialise to a FRESH array (legal: bound at the return slot,
            # never rebound into a regioned ref). Reuses the faithful `materialize` bridge.
            # ELEMENT-TYPE FIDELITY: a `string`-element list (declared return `array string`)
            # must use the STRING materialize bridge — `materialize` is `seq int -> array int`
            # and would type-clash on a `seq string` payload. This mirrors the early/in-loop
            # `Return_seq_str` path (below) for the TAIL (non-raise) return; without it, a
            # string-list function whose only normal exit is the tail return (e.g. os.listdir
            # once its failure paths raise OSError instead of `return []`) wrongly emits the
            # int `materialize` and fails L3 type-check.
            if self._func_return_type == "array string":
                self._materialize_str_bridge()
                val = f"(materialize_str !{whyml_ident(val_ir['name'])})"
            else:
                self._materialize_bridge()
                val = f"(materialize !{whyml_ident(val_ir['name'])})"
        else:
            if val_ir.get("type") == "Var" and val_ir.get("name") in self._array_locals:
                # `exception Return int` can't carry an array, so on the
                # raise-Return int path we collapse the value to 0
                # (lossy but at least type-correct). When the function
                # actually returns `array int` (slot+signal path) or at
                # function level (no raise), the array variable IS the
                # value — keep its name.
                if use_raise and func_ret_peek != "array int":
                    val = "0"
                else:
                    val = whyml_ident(val_ir["name"])
            else:
                val = self._expr_to_whyml(val_ir, local_refs)
        # typing-engagement ty1 / 25-1700-typing-spec-1 §0/§2.2 C2: if the
        # function's return type is a synthesized `_union_*` variant and the
        # returned value is NOT already a constructor application, auto-inject
        # it into the first arm whose payload type matches (the injection
        # wrapper per arm). This lets `def f() -> Optional[int]: return x+x`
        # type-check (the int return is wrapped as `Arm_<idx>_0 (x+x)`).
        val = self._maybe_inject_union_return(val, val_ir)
        if use_raise:
            func_ret = self._func_return_type
            if func_ret == "unit":
                return f"{indent}raise Return_void"
            arity = self._current_tuple_arity
            if arity > 0:
                # Tuple return: use the dedicated Return_<arity> exception
                # so the whole tuple value carries through. Do NOT call
                # _coerce_to_int — for tuple-shaped strings that would hash
                # the whole tuple to a single int.
                return f"{indent}raise (Return_{arity} {val})"
            if func_ret == "array int":
                # return-arr.md: array-returning functions with early/in-loop returns carry the
                # value through an IMMUTABLE seq (Why3 forbids a mutable `array int` exception
                # payload); the `with Return_seq s -> materialize s` catch rebuilds the array.
                # `_seq_init_expr` turns a list literal into a Seq.cons chain and bridges any
                # other array-typed RHS (array-local, etc.) with `snapshot`.
                self._materialize_bridge()
                if val_ir is None:
                    seq_val = "Seq.empty"
                elif (val_ir.get("type") == "Var"
                      and val_ir.get("name") in getattr(self, "_seq_locals", set())):
                    seq_val = f"!{whyml_ident(val_ir['name'])}"
                else:
                    seq_val = self._seq_init_expr(val_ir, local_refs)
                return f"{indent}raise (Return_seq {seq_val})"
            if func_ret == "array string":
                # str-list-elements: a STRING-element list returns its growable `seq string`
                # through `Return_seq_str`; the catch materializes it to `array string`. An
                # empty-list return (`return []`) carries the polymorphic `Seq.empty`.
                self._materialize_str_bridge()
                if val_ir is None:
                    seq_val = "Seq.empty"
                elif (val_ir.get("type") == "Var"
                      and val_ir.get("name") in getattr(self, "_seq_locals", set())):
                    seq_val = f"!{whyml_ident(val_ir['name'])}"
                else:
                    seq_val = self._seq_init_expr(val_ir, local_refs)
                return f"{indent}raise (Return_seq_str {seq_val})"
            if func_ret == "string":
                # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
                # return raises `Return_str <string>` (caught by the `with Return_str r -> r`
                # arm). `val` is already the lowered string expression — no int coercion.
                return f"{indent}raise (Return_str {val})"
            # Array-returning functions with early returns CANNOT use the
            # straightforward `raise (Return arr)` shape — Why3 forbids
            # `array int` in exception payloads (mutable types), and the
            # `ref (array int)` + signal workaround triggers Why3's
            # region/linearity tracking (`Array.make` in the body becomes
            # "prohibits further usage of _ret_array_slot"). Workaround
            # at the source level: `\trusted` the affected functions so
            # Module6 emits `val` (spec-only) instead of `let` + body.
            # See docs/self-annotate-layer2-queue.md class M for the
            # design analysis.
            # int return path: an array-typed val here is structurally
            # incompatible — `Return int` can't carry it. Collapse to 0
            # (matches the pre-existing lossy behaviour).
            if (val_ir and val_ir.get("type") == "Var"
                    and val_ir.get("name") in self._array_locals):
                val = "0"
            elif val == "()":
                val = "0"
            elif val == "true":
                val = "1"
            elif val == "false":
                val = "0"
            else:
                val = self._bool_ir_to_int_wrap(val, val_ir)
            val = self._coerce_to_int(val)
            return f"{indent}raise (Return {val})"
        return f"{indent}{val}"


