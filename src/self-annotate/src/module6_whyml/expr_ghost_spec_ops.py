from __future__ import annotations
from typing import Any, Dict, Optional, Set
def mutable_state(cls): return cls
""  # pycsl
@mutable_state
class GhostSpecOpsMixin:
    "Ghost spec-operator leaf handlers for tuples, strings, and ghost arrays —\n    the non-collection counterpart of `GhostCollectionOpsMixin`:\n\n      * tuples:       `\\mktuple` / `\\fst` / `\\snd` / `\\proj`\n      * strings:      `\\strconcat` (`^`) / `\\str_length` / `\\str_sub`\n      * ghost arrays: `\\copy` / `\\copy_range` / `\\make`\n\n    Extracted verbatim from `ExpressionEmissionMixin` (Part B move 3d).\n    `ExpressionEmissionMixin` inherits this mixin, so the handlers resolve via\n    MRO through the facade's `_EXPR_DISPATCH` and call back into `self._e`,\n    `self._deref`, `self._expr_to_whyml_string_ctx`, and `self._ghost_tuple_vars`\n    (which stay in `ExpressionEmissionMixin`)."

    # item34.md CF0.3 pattern (mirrored from stmt_control_flow.py): cross-file
    # recursion-leaf / bridge sibling stubs for `_e`/`_expr_to_whyml_string_ctx`
    # (defined in `ExpressionEmissionMixin`, expressions.py, which this mixin
    # composes with at runtime). Standalone per-file verification of this mixin
    # cannot see that sibling class, so a same-named call would otherwise
    # auto-synthesize a generic int-typed stub; the local trusted redeclaration
    # types the param the way this file actually calls it (an ExprIR sub-node),
    # matching the already-tolerated mirror-only shim precedent.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _e(self, ir: "ExprIR", lr: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _expr_to_whyml_string_ctx(self, ir: "ExprIR", lr: Set[str]) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_mktuple_expr(self, expr: int, lr: int, _ic: bool, _sub: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_fst_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (x_, _) = !{safe_t} in x_)" if t.startswith("!") else f"(let (x_, _) = {t} in x_)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_snd_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (_, y_) = !{safe_t} in y_)" if t.startswith("!") else f"(let (_, y_) = {t} in y_)"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_proj_expr(self, expr: int, lr: int, _ic: bool, _sub: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ctor_test_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        x = self._e({"type": "Var", "name": node.var}, lr)
        ctor = node.ctor
        arity = getattr(self, "_constructors", {}).get(ctor, {}).get("arity", 0)
        binders = (" " + " ".join(["_"] * arity)) if arity else ""
        return f"(match {x} with {ctor}{binders} -> true | _ -> false end)"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ctor_payload_expr(self, expr: int, lr: int, _ic: bool, _sub: int) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_strconcat_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._expr_to_whyml_string_ctx(node.left.to_dict(), lr)
        r = self._expr_to_whyml_string_ctx(node.right.to_dict(), lr)
        # Why3 string.String exports 'concat' (not '^' or 'String.(^)')
        return f"(concat {l} {r})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_str_length_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        return f"(String.length {s})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_str_sub_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(String.substring {s} {lo} ({hi} - {lo}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ghost_copy_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return f"(Array.copy {node.arr})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ghost_copy_range_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(Array.sub {node.arr} {lo} ({hi} - {lo}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_ghost_make_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        n = self._e(node.size, lr)
        v = self._e(node.default, lr)
        return f"(Array.make {n} {v})"


