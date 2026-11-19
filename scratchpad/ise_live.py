    def _is_string_expr(self, ir: Dict[str, Any]) -> bool:
        """True if an IR expression is string-typed: a literal, a string-producing op, or a
        `str`-typed variable. (strings-plan Stage 2 — used to route `+` to `concat`.)"""
        t = ir.get("type")
        # W8 capability (iii): a `str` field projected off an `array <record>` SELF-FIELD
        # element (`self.toks[self.i].string`, or `t.string` on the record-typed local
        # bound to such a read) is STRING-typed. Without this the projection keeps the
        # default int typing and a `== "EOF"` comparison coerces it to int (L3-tc:
        # `This expression has type string, but is expected to have type int`).
        if self._record_elem_field_py_type(ir) == "str":
            return True
        # resync-campaign.md R2: a ternary whose BOTH arms are string-typed is string (the
        # emitter's `(if _poly then "<decl A>" else "<decl B>") + "…ensures…"` concat). Both
        # arms must be string; @mutable_state (the emitter's string decls). Lever-7 extends the
        # gate: a both-arms-string ternary in an `Optional[str]`/`Union[…, str]`-returning
        # function (`_func_ret_union_some_str()`) is ALSO string-typed, so it injects into the
        # variant's string arm (`Arm_N_0 …`) at the return site instead of type-clashing the bare
        # ternary against the `_union_*` variant. Fail-closed on the union predicate → byte-inert.
        if (t == "IfExpr"
                and (getattr(self, "_current_self_type", None)
                     in getattr(self, "_mutable_state_classes", set())
                     or self._func_ret_union_some_str())
                and self._is_string_expr(ir.get("body", {}))
                and self._is_string_expr(ir.get("orelse", {}))):
            return True
        # string-bool-op: a both-operands-string `or`/`and` is itself STRING (Python's
        # `a or b`/`a and b` return one of the operands, not a bool) — so it types as a
        # string local / return and routes `+`, `.lower()`, etc. through the string ops.
        # The `or` right arm may be `None` (`<get> or ""` idiom, right modeled as "").
        # Both operands must be string; a mixed/bool/int operand keeps the non-string
        # (bool/int) typing (additivity). Subsumes the earlier @mutable_state `or` branch.
        if (t == "BinOp" and ir.get("op") in ("and", "or")
                and self._is_string_expr(ir.get("left", {}))
                and (self._is_string_expr(ir.get("right", {}))
                     or (ir.get("op") == "or"
                         and isinstance(ir.get("right"), dict)
                         and ir["right"].get("type") == "None"))):
            return True
        if t == "Call":
            _fn = ir.get("func", "")
            # G2 (09-2223 pure-classifier increment): `<record-var>.get("<str-field>")` is
            # STRING-typed (its G1 lowering is the native `func.kind : string`), so a
            # comparison `func.get("kind") == "method"` routes through `str_eq_op` — a
            # faithful string content compare — instead of the unfaithful int-hash
            # `(func_get_1 …) <> 317966025`. Gated on the record-typed receiver + a `str`
            # field via `_record_get_field` (never a plain dict), so it is corpus-byte-inert.
            _rg = self._record_get_field(ir)
            if _rg is not None and _rg[2] == "str":
                return True
            # option-of-record projection (boundary-1 G1 extension): `<optvar>.get("<str-
            # field>")` on an `Optional[<record>]` receiver is STRING-typed (the Some arm
            # projects `_r.<label> : string`), so `optvar.get("type") == "Compare"` routes
            # through `str_eq_op`, not the int-hash. Gated on `_option_record_get_field`.
            _org = self._option_record_get_field(ir)
            if _org is not None and _org[2] == "str":
                return True
            # `str(x)` is string-typed (identity on a str, `int_to_string` on an int) — so a
            # `.lower()`/`.strip()` on it (`str(binder_type).lower()`) recognizes as a faithful
            # string-value method rather than falling to the opaque scalar op.
            if _fn == "str":
                return True
            # faithful-string-op.md §3.1–3.3: `.replace`/`.lower`/`.upper`/`.strip` on a
            # string receiver is itself string-typed, so a receiving local (`arr_name =
            # func.rsplit(".",1)[0].replace(".","_")`) types as a string local.
            if self._is_str_value_method(ir):
                return True
            # §3.5: a literal-string-list `sep.join([…])` is string (nested concat).
            if self._is_literal_string_join(ir):
                return True
            # list-comprehension-lowering.md L2: a general `sep.join(<string-array>)` is a
            # `string` (str_join_arr), so `"(" + ",".join(xs) + ")"` routes `+` to concat.
            if ((_fn == "join" or (isinstance(_fn, str) and _fn.endswith(".join")))
                    and self._join_arg_elem_is_string(
                        (ir.get("args") or [{}])[0] if ir.get("args") else {})):
                return True
            # typed-ir-for-b-ceiling.md §14: `getattr(self, "<field>", <default>).get(k)`
            # on a `dict[str,str]` field reads back a `string` — the getattr-defensive
            # form of the §12 self-field-dict get (func is bare `"get"` with a `getattr`
            # receiver, before the §14 rewrite).
            if _fn == "get":
                # subscript-receiver .get with a STRING key (`a[i].get("name")`/`.get("type")`) on an
                # emit_ir element → a string projection (name_of/kind_of/func_of/value_of), so a
                # `== "self"` comparison routes through str_eq_op. @mutable_state / emit_ir-gated.
                _grcv = ir.get("receiver")
                if isinstance(_grcv, dict) and self._is_emit_ir_expr(_grcv):
                    _gk = (ir.get("args") or [{}])[0]
                    # self-tcb-reduction (_is_null_byte_lit): a Number element's `.get("value")`
                    # there reads the INT payload (`num_of`), so it is NOT string-typed — the
                    # `== 0` comparison must stay an int `=`, not the mixed str_hash_op path.
                    # Scoped via `_current_emitting_func` → corpus/consumer-inert.
                    if (isinstance(_gk, dict) and _gk.get("type") == "String"
                            and _gk.get("value") in _EMIT_IR_STR_KEYS + ("value",)
                            and not (_gk.get("value") == "value"
                                     and (getattr(self, "_current_emitting_func", None) or "")
                                     .endswith("_is_null_byte_lit"))):
                        return True
                _gf = self._getattr_self_field(ir.get("receiver"))
                if _gf and self._self_field_dict_nu(f"self.{_gf}") == "string":
                    return True
            if _fn.endswith(".get"):
                # item34.md CF5: `<handler>.get("exc_type")` — a 1-arg string-key `.get` on a
                # NON-emit_ir receiver reads a string scalar field (matches `_grecv_str`).
                _gargs = ir.get("args") or []
                if (len(_gargs) == 1 and isinstance(_gargs[0], dict)
                        and _gargs[0].get("type") == "String"
                        and getattr(self, "_current_self_type", None)
                        in getattr(self, "_mutable_state_classes", set())
                        and not self._is_emit_ir_expr(
                            {"type": "Var", "name": _fn[:-len(".get")]})):
                    return True
                # self-field-dict-reflection (typed-ir §12): `self.<dict[str,str]-field>
                # .get(k)` reads back a `string` (`option string` values), so `… == "s"`
                # routes through `str_eq_op`, not an int hash.
                if self._self_field_dict_nu(_fn[:-len(".get")]) == "string":
                    return True
                # §26: `X.get(k)` where X aliases a `dict[str,str]` self-field reads a string.
                _alias0 = self._alias_self_field(_fn[:-len(".get")])
                if _alias0 and self._self_field_dict_nu(_alias0) == "string":
                    return True
                _al = getattr(self, "_todict_aliases", {}).get(_fn[:-len(".get")])
                if _al is not None:
                    _kir = (ir.get("args") or [{}])[0]
                    if isinstance(_kir, dict) and _kir.get("type") == "String":
                        if self._is_emit_ir_expr(self._todict_recv_node_ir(_al)):
                            return _kir.get("value") in _EMIT_IR_STR_KEYS
                        return self._is_string_expr(
                            self._todict_routed_ir(_al, _kir.get("value")))
                # typed-ir-for-b-ceiling.md B-C3: `<emit_ir>.get("type"|"name"|"attr"|
                # "value")` projects to `kind_of`/`name_of`/`value_of` — all `string` —
                # so `node.get("type") == "Var"` routes through `str_eq_op`, not an int
                # hash. (`"object"` is emit_ir, not string → not matched here.)
                _rn = _fn[:-len(".get")]
                if self._is_emit_ir_expr({"type": "Var", "name": _rn}):
                    _kir = (ir.get("args") or [{}])[0]
                    if (isinstance(_kir, dict) and _kir.get("type") == "String"
                            and _kir.get("value") in _EMIT_IR_STR_KEYS):
                        return True
        if t == "String" or t in ("StrConcat", "StrSub"):
            return True
        if t == "Var":
            _vn = ir.get("name", "")
            # self-tcb-reduction T1.a: a collected string LOCAL (`var = node.var` → name_of) counts
            # as string even before its symbol-table type is set, so `var in self._seq_locals`
            # hashes the key. Byte-safe: `_string_local_vars` is empty outside @mutable_state.
            return (getattr(self, "_current_symbol_table", {}).get(_vn) == "str"
                    or _vn in getattr(self, "_string_local_vars", set()))
        # Indexing/slicing a string yields a string (s[i] is a 1-char string, s[a:b] a
        # substring) — both reuse str_sub_op in their handlers, so the *result* of such a
        # node is string-typed exactly when its base is. Required so `s[a:b] == t` routes to
        # the real string-equality bridge rather than the mixed int-hash fallback (0471).
        if t in ("Subscript", "SliceAccess"):
            # faithful-string-op.md §3.4: a split-element read `<string>.split(sep)[i]` is
            # a substring → string-typed, even though the split CALL itself is a list.
            if self._split_call_recv_sep(ir.get("value", {})) is not None:
                return True
            # §26: subscript-form emit_ir string-projection `<emit_ir>["type"/"name"/
            # "attr"/"func"]` (the string keys) → string, for `arr["value"]["name"]`.
            # cf6.md M1.3: EXCLUDE node keys — as a SUBSCRIPT `c["pattern"]` reads a sub-NODE,
            # not the kind string (only `.get("pattern")` is the kind).
            _kir = ir.get("index", {})
            if (isinstance(_kir, dict) and _kir.get("type") == "String"
                    and (_kir.get("value") in _EMIT_IR_STR_KEYS or _kir.get("value") == "object")
                    and (_kir.get("value") not in _EMIT_IR_NODE_KEYS or _kir.get("value") == "object")
                    and self._is_emit_ir_expr(ir.get("value", {}))):
                return True
            # list-comprehension-lowering.md L5/L6: a `self.<dict[str,str]-field>[k]` read
            # (`self._abstract_ops[k]`) or a string-element array-local index (`safe[i]`)
            # is a string.
            _v = ir.get("value", {})
            if isinstance(_v, dict):
                if _v.get("type") in ("Attribute", "FieldGet"):
                    _o = _v.get("object"); _f = _v.get("field") or _v.get("attr")
                    if isinstance(_o, str) and self._self_field_dict_nu(f"{_o}.{_f}") == "string":
                        return True
                if (_v.get("type") == "Var"
                        and getattr(self, "_array_elem_types", {}).get(_v.get("name")) == "string"):
                    return True
                # self-ir-schema.md IR3: `sv["name"]`/`sv["mutex"]` on a `sharedvar`-typed
                # comprehension loop var → the record's string field (used only for
                # element-type inference; the comprehension itself is opaque).
                if (_v.get("type") == "Var"
                        and getattr(self, "_current_symbol_table", {}).get(_v.get("name")) == "sharedvar"
                        and _kir.get("value") in ("name", "mutex")):
                    return True
            return self._is_string_expr(ir.get("value", {}))
        # `s + t` is a `BinOp(+)` node (string concatenation when both operands are
        # strings) — so a concat expression is itself string-typed. Required so e.g.
        # `len(s + t)` routes to str_length_op rather than the opaque iter_length.
        if t == "BinOp" and ir.get("op") == "+":
            return (self._is_string_expr(ir.get("left", {}))
                    and self._is_string_expr(ir.get("right", {})))
        # 10-1732-gap (Gap 2): a `Call` to a module function (incl. an injected
        # imported `\trusted` stub) declared `-> str` is itself string-typed. Required
        # so `len(g(s))` routes to str_length_op rather than the opaque iter_length.
        # Keyed on the SEPARATE `_module_method_return_annotations` map (Python
        # `return_annotation == "str"`), NOT `_module_method_return_types` — the latter
        # is a stripped map that leaves `-> str` callees as "int" (see the wiring note
        # in Module6_WhyMLTranspiler.transpile). A lookup MISS (builtin/unresolved name)
        # yields None != "str" → safe False (unchanged opaque path).
        if t == "Call":
            fn = ir.get("func", "")
            # 10-2300-spec-5: `chr(...)` yields a 1-char string (chr_op : ... -> string).
            # So `len(chr(b))`, `s + chr(b)`, `chr(b) == c`, and `chr(...)` as a subscript
            # base route through the real string bridges, not the opaque int fallback.
            # (`ord(...)` is int → default `False` below, no edit needed.)
            if fn == "chr":
                return True
            # no-more-int emitter L4: a `self.<m>(…)` call keys the return-annotation
            # map by the class-qualified name (`<self_type>__<m>`, as `_handle_dotted_
            # call` does), so a `str`-returning sibling emitter (`self._stmts_to_whyml`,
            # `self._expr_to_whyml`) is recognized as string — routing `s + <call>` to
            # concat. A bare call is keyed by its name (unchanged).
            ann = getattr(self, "_module_method_return_annotations", {})
            if fn.startswith("self."):
                tail = fn[len("self."):]
                cls = getattr(self, "_current_self_type", None)
                key = f"{cls}__{tail}" if cls else tail
            else:
                key = fn
            return ann.get(key) == "str"
        # todict-reflection-plan.md R3: in a @mutable_state class (the emitter model) an
        # f-string is string-typed — `_handle_fstring_expr` there lowers every f-string
        # (all-string OR mixed str/int via `int_to_string`) to a `string`. So a string
        # target's `code += f"…"` routes to `str_concat_op`. Gated on @mutable_state →
        # byte-identical for every other f-string.
        if t == "FString":
            return (bool(ir.get("parts"))
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set()))
        # todict-reflection-plan.md: a record's `str`-typed FIELD read (`n.kind` on a
        # record-typed param/local, or `self.f`/`global.f`) is string-typed — so
        # `n.kind == "Var"` routes to `str_eq_op`, not the int-hash mismatch. self/
        # global/record-var via `_field_type_of`; a record-typed PARAM/local via the
        # symbol table + the record's `field_types`. A non-str/unknown field → False
        # (unchanged opaque path) → byte-identical outside genuine str-field reads.
        if t in ("Attribute", "FieldGet"):
            # J2/J3 convergence (Call-internals): the string-producing keyword/call reads
            # `kw.arg`, `kw.value.id`, `kw.value.attr` and `<emit_ir call>.func.id` are
            # `string`, so `kw.arg == "bound"` / `call.func.id == "TypeVar"` route through
            # `str_eq_op` (faithful content compare), not the int-hash. Corpus-inert.
            if t == "Attribute":
                _attr = ir.get("attr")
                _o = ir.get("object", {})
                # W8 capability (vi): `self.cur().string` projects a `str` field off a
                # RECORD-returning sibling call, so the comparison must route through
                # `str_eq_op` (faithful content compare) rather than collapsing the
                # projection to the legacy int hash. Same `_record_array_fields` gate as
                # the emission branch in `_handle_attribute_expr` → byte-inert elsewhere.
                if (isinstance(_o, dict) and _o.get("type") == "Call"
                        and isinstance(_o.get("func"), str)
                        and _o["func"].startswith("self.")
                        and getattr(self, "_record_array_fields", None)):
                    _crt = self._resolve_dotted_signature(_o["func"])[0]
                    for _rc, _ri in getattr(self, "_record_types", {}).items():
                        if _ri.get("whyml_name") == _crt:
                            if _ri.get("field_types", {}).get(_attr) in ("str", "string"):
                                return True
                            break
                # K2 convergence (self-tcb-reduction): `<pyast_stmt local>.name` projects
                # to `def_name` — the ClassDef/FunctionDef NAME, a `string` — so
                # `cstmt.name == "__init__"` routes through `str_eq_op` (faithful content
                # compare, not the int-hash) and a `"class": stmt.name` dict value wraps as
                # `PStr`, not `PInt`. `.target`/`.value`/`.annotation` project to emit_ir
                # (handled below via `_is_emit_ir_expr`), so ONLY `.name` is string here.
                if (_attr == "name"
                        and self._pyast_stmt_child_var(_o) is not None):
                    return True
                if (getattr(self, "_keyword_locals", None)
                        and _attr == "arg" and self._keyword_var(_o) is not None):
                    return True
                if (getattr(self, "_keyword_locals", None) and _attr in ("id", "attr")
                        and isinstance(_o, dict) and _o.get("type") == "Attribute"
                        and _o.get("attr") == "value"
                        and self._keyword_var(_o.get("object", {})) is not None):
                    return True
                if (_attr == "id" and isinstance(_o, dict)
                        and _o.get("type") == "Attribute" and _o.get("attr") == "func"
                        and isinstance(_o.get("object"), dict)
                        and _o["object"].get("type") == "Var"
                        and _o["object"].get("name")
                        in getattr(self, "_emit_ir_local_vars", set())):
                    return True
            ft = self._field_type_of(ir)
            # self-tcb-reduction T1.a: a STRING-valued emit_ir attr (`.kind`/`.var`/`.op`/…) reads a
            # discriminant/name string, so `inner.kind == "Subscript"` routes through `str_eq_op`.
            if ft is None and (ir.get("attr") or ir.get("field")) in _EMIT_IR_STR_ATTRS:
                _ko = ir.get("value") or ir.get("object")
                if isinstance(_ko, dict) and self._is_emit_ir_expr(_ko):
                    return True
            if ft is None:
                if t == "FieldGet":
                    _rn, _fl = ir.get("object"), ir.get("field")
                else:
                    _r = ir.get("value") or ir.get("object")
                    _rn = _r.get("name") if isinstance(_r, dict) else None
                    _fl = ir.get("attr")
                if isinstance(_rn, str):
                    _rt = getattr(self, "_current_symbol_table", {}).get(_rn)
                    if _rt and _rt in getattr(self, "_record_types", {}):
                        ft = self._record_types[_rt].get("field_types", {}).get(_fl)
            return ft in ("str", "string")
        return False

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

