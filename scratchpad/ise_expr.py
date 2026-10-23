    def _is_string_expr(self, ir: "ExprIR") -> bool:
        return False
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _is_float_expr(self, ir: "ExprIR") -> bool:
        """True if an IR expression is float-typed (no-more-int Stage D): a float literal,
        a `float`-typed Var, or float arithmetic. Routes ops to Why3 `real`."""
        t = ir.get("type")
        if t == "Number":
            return isinstance(ir.get("value"), float)
        if t == "Var":
            return getattr(self, "_current_symbol_table", {}).get(ir.get("name", "")) == "float"
        if t == "BinOp" and ir.get("op") in ("+", "-", "*", "/"):
            return (self._is_float_expr(ir.get("left", {}))
                    and self._is_float_expr(ir.get("right", {})))
        return False
    # str(<int>) value-model increment (self-tcb-reduction M6, C-bucket): now that
    # `str(<int>)` lowers to `str_of_int : int -> string`, a quoted-literal string operand
    # hashes to its decimal `str(stable_hash(...))`; a non-literal goes through the
    # uninterpreted `str_hash_op`. isinstance_op = 0. Verbatim body port of the LIVE
    # `_str_operand_to_int`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
