from __future__ import annotations

from typing import Any, Dict, Optional, Set


class GhostCollectionOpsMixin:
    """Ghost-collection spec-operator handlers — the `\\map_*` / `\\set_*` and
    ghost-list (`\\nil`/`\\cons`/`\\hd`/`\\tl`/`\\list_length`/`\\nth`/`\\mem`/`++`)
    expression handlers, each emitting a fixed Why3 form over the
    `map int (option int)` / `map int bool` / `list int` models.

    Extracted verbatim from `ExpressionEmissionMixin` (Part B move 3c, mirroring
    the module5/ split). `ExpressionEmissionMixin` inherits this mixin, so the
    handlers resolve via MRO through the facade's `_EXPR_DISPATCH` and call back
    into `self._e` / `self._deref` (which stay in `ExpressionEmissionMixin`)."""

    def _handle_map_empty_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: absent keys map to None
        return "(const (None: option int))"

    def _handle_map_get_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = self._deref(d)
        return f"(match Map.get {d_r} {k} with | Some v_ -> v_ | None -> 0 end)"

    def _handle_map_set_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        v = self._e(expr["value"], lr)
        d_r = self._deref(d)
        return f"(Map.set {d_r} {k} (Some {v}))"

    def _handle_map_eq_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall k_: int. Map.get {l_r} k_ = Map.get {r_r} k_)"

    def _handle_has_key_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # option-type design: key is present iff its value is Some (not None)
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = self._deref(d)
        return f"(Map.get {d_r} {k} <> None)"

    def _handle_map_remove_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        d = self._e(expr["dict"], lr)
        k = self._e(expr["key"], lr)
        d_r = self._deref(d)
        return f"(Map.set {d_r} {k} None)"

    def _handle_set_empty_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        # Why3: map.Const exports 'const', not 'Map.const'
        return "(const false)"

    def _handle_set_add_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        e = self._e(expr["elem"], lr)
        s_r = self._deref(s)
        return f"(Map.set {s_r} {e} true)"

    def _handle_set_remove_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        e = self._e(expr["elem"], lr)
        s_r = self._deref(s)
        return f"(Map.set {s_r} {e} false)"

    def _handle_set_mem_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(expr["elem"], lr)
        s_ir = expr["set"]
        s_t = s_ir.get("type", "") if isinstance(s_ir, dict) else ""
        if s_t in ("SetUnion", "SetInter", "SetDiff"):
            # Functional set (lambda int -> bool) — use direct application, not Map.get
            s = self._e(s_ir, lr)
            return f"({s} {e})"
        s = self._e(s_ir, lr)
        s_r = self._deref(s)
        return f"(Map.get {s_r} {e})"

    def _handle_set_union_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_su"
        # Use parenthesised parameter for validity in both program and spec contexts
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) || (Map.get {r_r} {v}))"

    def _handle_set_inter_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_si"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && (Map.get {r_r} {v}))"

    def _handle_set_diff_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_sd"
        return f"(fun ({v}: int) -> (Map.get {l_r} {v}) && not (Map.get {r_r} {v}))"

    def _handle_set_card_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._e(expr["set"], lr)
        lo = self._e(expr["lo"], lr)
        hi = self._e(expr["hi"], lr)
        s_r = self._deref(s)
        return f"(set_card {s_r} {lo} {hi})"

    def _handle_set_subset_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_ss"
        return f"(forall {v}: int, Map.get {l_r} {v} -> Map.get {r_r} {v})"

    def _handle_set_eq_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        v = "_k_se"
        # Why3 forall uses '.' as body separator, not ','
        return f"(forall {v}: int. Map.get {l_r} {v} = Map.get {r_r} {v})"

    def _handle_nil_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return "Nil"

    def _handle_cons_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        h = self._e(expr["head"], lr)
        t = self._e(expr["tail"], lr)
        t_r = self._deref(t)
        return f"(Cons {h} {t_r})"

    def _handle_hd_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = self._deref(l)
        return f"(match {l_r} with | Cons h_ _ -> h_ | Nil -> absurd end)"

    def _handle_tl_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = self._deref(l)
        return f"(match {l_r} with | Cons _ t_ -> t_ | Nil -> absurd end)"

    def _handle_list_length_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        l_r = self._deref(l)
        # Why3 list.Length theory exports 'length', not 'List.length'
        return f"(length {l_r})"

    def _handle_nth_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["list"], lr)
        i = self._e(expr["index"], lr)
        l_r = self._deref(l)
        # Why3 list.NthNoOpt exports 'nth: int -> list 'a -> 'a' (partial, axioms nth_cons_0/nth_cons_n)
        return f"(nth {i} {l_r})"

    def _handle_mem_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        e = self._e(expr["elem"], lr)
        l = self._e(expr["list"], lr)
        l_r = self._deref(l)
        # Why3 list.Mem exports 'mem', not 'List.mem'
        return f"(mem {e} {l_r})"

    def _handle_append_expr(self, expr: Dict[str, Any], lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._e(expr["left"], lr)
        r = self._e(expr["right"], lr)
        l_r = self._deref(l)
        r_r = self._deref(r)
        # Why3 list.Append exports '(++)', not 'List.(++)'
        return f"({l_r} ++ {r_r})"
