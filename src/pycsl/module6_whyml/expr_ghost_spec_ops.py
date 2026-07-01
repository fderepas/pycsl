from __future__ import annotations

from typing import Any, Dict, Optional, Set


class GhostSpecOpsMixin:
    """Ghost spec-operator leaf handlers for tuples, strings, and ghost arrays —
    the non-collection counterpart of `GhostCollectionOpsMixin`:

      * tuples:       `\\mktuple` / `\\fst` / `\\snd` / `\\proj`
      * strings:      `\\strconcat` (`^`) / `\\str_length` / `\\str_sub`
      * ghost arrays: `\\copy` / `\\copy_range` / `\\make`

    Extracted verbatim from `ExpressionEmissionMixin` (Part B move 3d).
    `ExpressionEmissionMixin` inherits this mixin, so the handlers resolve via
    MRO through the facade's `_EXPR_DISPATCH` and call back into `self._e`,
    `self._deref`, `self._expr_to_whyml_string_ctx`, and `self._ghost_tuple_vars`
    (which stay in `ExpressionEmissionMixin`)."""

    def _handle_mktuple_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        parts = ", ".join(self._e(e, lr) for e in node.elts)
        return f"({parts})"

    def _handle_fst_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (x_, _) = !{safe_t} in x_)" if t.startswith("!") else f"(let (x_, _) = {t} in x_)"

    def _handle_snd_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        safe_t = t.lstrip("!")
        return f"(let (_, y_) = !{safe_t} in y_)" if t.startswith("!") else f"(let (_, y_) = {t} in y_)"

    def _handle_proj_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        t = self._e(node.tuple, lr)
        idx = int(node.index)
        # Infer arity from ghost_tuple_vars; fall back to idx+1 (minimum valid)
        var_name = node.tuple.to_dict().get("name", "")
        arity = self._ghost_tuple_vars.get(var_name, max(2, idx + 1))
        slots = ["_"] * arity
        if idx < arity:
            slots[idx] = "z_"
        pattern = ", ".join(slots)
        t_deref = self._deref(t)
        return f"(let ({pattern}) = {t_deref} in z_)"

    def _handle_ctor_test_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        """A5b: `\\is_ctor(x, Ctor)` — datatype discriminator, lowered to a Why3
        match term `match x with Ctor _ … -> true | _ -> false`. Arity comes
        from the constructor registry."""
        x = self._e({"type": "Var", "name": node.var}, lr)
        ctor = node.ctor
        arity = getattr(self, "_constructors", {}).get(ctor, {}).get("arity", 0)
        binders = (" " + " ".join(["_"] * arity)) if arity else ""
        return f"(match {x} with {ctor}{binders} -> true | _ -> false end)"

    def _handle_ctor_payload_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        """A5b: `\\payload(x, Ctor)` — datatype projector for the (first) payload,
        lowered to `match x with Ctor v … -> v | _ -> <default>`. Scoped to a
        concrete (int/str) payload type so the fall-through default is well-typed;
        a type-parameter payload needs an `\\is_ctor` guard (the `_` arm would not
        typecheck) — documented boundary."""
        x = self._e({"type": "Var", "name": node.var}, lr)
        ctor = node.ctor
        idx = int(node.index)
        info = getattr(self, "_constructors", {}).get(ctor, {})
        payload = info.get("payload", [])
        arity = info.get("arity", len(payload))
        if arity == 0 or idx >= arity:
            return "0"   # nullary / out-of-range — no payload
        binders = ["_"] * arity
        binders[idx] = "z_"   # bind the i-th payload, others `_`
        ptype = payload[idx] if idx < len(payload) else "int"
        default = '""' if ptype == "str" else "0"
        return f"(match {x} with {ctor} {' '.join(binders)} -> z_ | _ -> {default} end)"

    def _handle_strconcat_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        l = self._expr_to_whyml_string_ctx(node.left.to_dict(), lr)
        r = self._expr_to_whyml_string_ctx(node.right.to_dict(), lr)
        # Why3 string.String exports 'concat' (not '^' or 'String.(^)')
        return f"(concat {l} {r})"

    def _handle_str_length_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        return f"(String.length {s})"

    def _handle_str_sub_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        s = self._expr_to_whyml_string_ctx(node.string.to_dict(), lr)
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(String.substring {s} {lo} ({hi} - {lo}))"

    def _handle_ghost_copy_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        return f"(Array.copy {node.arr})"

    def _handle_ghost_copy_range_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        lo = self._e(node.lo, lr)
        hi = self._e(node.hi, lr)
        return f"(Array.sub {node.arr} {lo} ({hi} - {lo}))"

    def _handle_ghost_make_expr(self, node: "ExprIR", lr: Set[str], _ic: bool, _sub: Optional[Dict[str, str]]) -> str:
        n = self._e(node.size, lr)
        v = self._e(node.default, lr)
        return f"(Array.make {n} {v})"
