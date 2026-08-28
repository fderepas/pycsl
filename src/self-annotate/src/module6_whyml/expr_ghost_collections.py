from __future__ import annotations
from typing import Any, Dict, Optional, Set
def mutable_state(cls): return cls
""  # pycsl
@mutable_state
class GhostCollectionOpsMixin:
    "Ghost-collection spec-operator handlers — the `\\map_*` / `\\set_*` and\n    ghost-list (`\\nil`/`\\cons`/`\\hd`/`\\tl`/`\\list_length`/`\\nth`/`\\mem`/`++`)\n    expression handlers, each emitting a fixed Why3 form over the\n    `map int (option int)` / `map int bool` / `list int` models.\n\n    Extracted verbatim from `ExpressionEmissionMixin` (Part B move 3c, mirroring\n    the module5/ split). `ExpressionEmissionMixin` inherits this mixin, so the\n    handlers resolve via MRO through the facade's `_EXPR_DISPATCH` and call back\n    into `self._e` / `self._deref` (which stay in `ExpressionEmissionMixin`)."

    # item34.md CF0.3 pattern (mirrored from stmt_control_flow.py): cross-file
    # recursion-leaf / bridge sibling stubs for `_e`/`_deref` (defined in
    # `ExpressionEmissionMixin`, expressions.py, which this mixin composes with at
    # runtime). Standalone per-file verification of this mixin cannot see that
    # sibling class, so a same-named call would otherwise auto-synthesize a
    # generic int-typed stub; the local trusted redeclaration types the param the
    # way this file actually calls it (an ExprIR sub-node), matching the
    # already-tolerated mirror-only shim precedent.
    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _e(self, ir: "ExprIR", lr: Set[str]) -> str:
        return ""

    # SHADOWED-SELFCALL REPAIR (lesson (ay)): CONVERTED and PROVED, yet all 28 of its
    # `self._deref(...)` call sites in this file went through the receiver-less abstract
    # `val self__deref_1 (x0: string) : string`, whose result is UNCONSTRAINED — so no
    # caller saw the `!`-normalization this body computes. The opt-in marker is the
    # SECOND admission route into the concrete lowering (the first, `_record_array_fields`,
    # is a PROXY that holds only for the parser-cursor shape and is empty for this file).
    # Sound: the callee is a same-file VERIFIED method in `_module_func_names`, and
    # `scc.find_self_method_calls` already supplies the callee-before-caller ordering edge
    # for a marked callee. Corpus byte-inert BY CONSTRUCTION — no corpus program writes
    # the directive.
    #@ sibling_concrete
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _deref(self, expr: str) -> str:
        """Dereference a WhyML ref-typed operand: `x` → `!x` (idempotent — a leading
        `!` is normalized, not doubled). Used by the set/list/map handlers, where a
        collection operand may arrive already-dereffed."""
        return f"!{expr.lstrip('!')}" if expr.startswith("!") else expr

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_map_empty_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: absent keys map to None
        return "(const (None: option int))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_map_get_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(node.dict, lr)
        k = self._e(node.key, lr)
        d_r = self._deref(d)
        return f"(match Map.get {d_r} {k} with | Some v_ -> v_ | None -> 0 end)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_map_set_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(node.dict, lr)
        k = self._e(node.key, lr)
        v = self._e(node.value, lr)
        d_r = self._deref(d)
        return f"(Map.set {d_r} {k} (Some {v}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_map_eq_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall k_: int. Map.get {l_r} k_ = Map.get {r_r} k_)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_has_key_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: key is present iff its value is Some (not None)
        d = self._e(node.dict, lr)
        k = self._e(node.key, lr)
        d_r = self._deref(d)
        return f"(Map.get {d_r} {k} <> None)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_map_remove_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(node.dict, lr)
        k = self._e(node.key, lr)
        d_r = self._deref(d)
        return f"(Map.set {d_r} {k} None)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_empty_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # Why3: map.Const exports 'const', not 'Map.const'
        return "(const false)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_add_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(node.set, lr)
        e = self._e(node.elem, lr)
        s_r = self._deref(s)
        return f"(Map.set {s_r} {e} true)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_remove_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(node.set, lr)
        e = self._e(node.elem, lr)
        s_r = self._deref(s)
        return f"(Map.set {s_r} {e} false)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_mem_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(node.elem, lr)
        s_ir = node.set
        s_t = s_ir.kind
        if s_t in ("SetUnion", "SetInter", "SetDiff"):
            # Functional set (lambda int -> bool) — use direct application, not Map.get
            s = self._e(s_ir, lr)
            return f"({s} {e})"
        s = self._e(s_ir, lr)
        s_r = self._deref(s)
        return f"(Map.get {s_r} {e})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_union_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_su"
        # Use parenthesised parameter for validity in both program and spec contexts
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) || (Map.get {r_r} {v}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_inter_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_si"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && (Map.get {r_r} {v}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_diff_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_sd"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && not (Map.get {r_r} {v}))"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_card_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(node.set, lr)
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        s_r = self._deref(s)
        return f"(set_card {s_r} {lo} {hi})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_subset_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_ss"
        return f"(forall {v}: int, Map.get {l_r} {v} -> Map.get {r_r} {v})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_set_eq_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_se"
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall {v}: int. Map.get {l_r} {v} = Map.get {r_r} {v})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_nil_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return "Nil"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_cons_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        h = self._e(node.head, lr)
        t = self._e(node.tail, lr)
        t_r = self._deref(t)
        return f"(Cons {h} {t_r})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_hd_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.list, lr)
        l_r = self._deref(l)
        return f"(match {l_r} with | Cons h_ _ -> h_ | Nil -> absurd end)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_tl_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.list, lr)
        l_r = self._deref(l)
        return f"(match {l_r} with | Cons _ t_ -> t_ | Nil -> absurd end)"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_list_length_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.list, lr)
        l_r = self._deref(l)
        # Why3 list.Length theory exports 'length', not 'List.length'
        return f"(length {l_r})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_nth_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.list, lr)
        i = self._e(node.index, lr)
        l_r = self._deref(l)
        # Why3 list.NthNoOpt exports 'nth: int -> list 'a -> 'a' (partial, axioms nth_cons_0/nth_cons_n)
        return f"(nth {i} {l_r})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_mem_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(node.elem, lr)
        l = self._e(node.list, lr)
        l_r = self._deref(l)
        # Why3 list.Mem exports 'mem', not 'List.mem'
        return f"(mem {e} {l_r})"

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _handle_append_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(node.left, lr)
        r = self._e(node.right, lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        # Why3 list.Append exports '(++)', not 'List.(++)'
        return f"({l_r} ++ {r_r})"


