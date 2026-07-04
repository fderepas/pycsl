from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from module6_whyml.identifiers import op_translate, whyml_ident, stable_hash, whyml_string_literal
from ir_schema import (
    expr_from_dict, _expr_from_dict_inner, OpaqueExpr,
    NumberExpr, StringExpr, ResultExpr, NoneExpr, RawWhymlExpr, BoolExpr,
    UnknownPyExprExpr, SliceExpr, OldFieldExpr, StarredExpr, TupleExpr,
    ArrayLitExpr, ForallExpr, ExistsExpr, MapValueIsExpr, VarExpr, FieldGetExpr,
    DictLitExpr, ListCompExpr, SetCompExpr, DictCompExpr, ForallItemsExpr,
)

# Phase-B-expr: handlers migrated to accept a typed ExprIR node (rather than the
# wire dict). The `_expr_to_whyml` tail dispatch passes the typed `node` to these
# and the legacy dict to the rest; an OpaqueExpr (a node carrying extra
# attribution keys the class doesn't model, e.g. BinOp+act_name) is coerced to
# its typed class via `_expr_from_dict_inner` — safe because these handlers do
# not read attribution keys. Grows one handler at a time, byte-diff gated.
_TYPED_EXPR_HANDLERS = {
    "_handle_unaryop_expr",
    "_handle_old_expr",
    "_handle_at_expr",
    "_handle_named_expr_expr",
    "_handle_ifexpr_expr",
    # ghost-collection ops (map/set/list) — expr_ghost_collections.py
    "_handle_map_empty_expr",
    "_handle_map_get_expr",
    "_handle_map_set_expr",
    "_handle_map_eq_expr",
    "_handle_has_key_expr",
    "_handle_map_remove_expr",
    "_handle_set_empty_expr",
    "_handle_set_add_expr",
    "_handle_set_remove_expr",
    "_handle_set_mem_expr",
    "_handle_set_union_expr",
    "_handle_set_inter_expr",
    "_handle_set_diff_expr",
    "_handle_set_card_expr",
    "_handle_set_subset_expr",
    "_handle_set_eq_expr",
    "_handle_nil_expr",
    "_handle_cons_expr",
    "_handle_hd_expr",
    "_handle_tl_expr",
    "_handle_list_length_expr",
    "_handle_nth_expr",
    "_handle_mem_expr",
    "_handle_append_expr",
    # ghost spec ops (tuple/ctor/str/array) — expr_ghost_spec_ops.py
    "_handle_mktuple_expr",
    "_handle_fst_expr",
    "_handle_snd_expr",
    "_handle_proj_expr",
    "_handle_ctor_test_expr",
    "_handle_ctor_payload_expr",
    "_handle_strconcat_expr",
    "_handle_str_length_expr",
    "_handle_str_sub_expr",
    "_handle_ghost_copy_expr",
    "_handle_ghost_make_expr",
    # misc spec/expr handlers
    "_handle_fstring_expr",
    "_handle_attribute_expr",
    "_handle_subscript",
    "_handle_call_expr",
    "_handle_binop",
    "_handle_arrayeq_expr",
    "_handle_permutation_expr",
    "_handle_separated_expr",
    "_handle_valid2d_expr",
    "_handle_length2d_expr",
    "_handle_slice_access_expr",
    "_handle_arraylen_expr",
    "_handle_issorted_expr",
    "_handle_sum_node_expr",
    "_handle_ghost_copy_range_expr",
    "_handle_valid_expr",
    "_handle_setlit_expr",
    "_handle_lambda_expr",
    "_handle_in_globals_expr",
    "_handle_in_scope_expr",
}

# i-feel-good.md I-D: the ONE emit_ir reflection projection map + key classes, defined
# once and referenced by every reflection site (dotted `.get`, subscript `["k"]`, nested,
# and the string-typedness checks). A reflection key maps to its total projection over the
# `emit_ir` sum; string-valued keys yield a `string`, sub-node keys yield an `emit_ir`.
# ("field" is the FieldGet member-name — a string, routed like "attr"/"name".)
_EMIT_IR_PROJ = {
    "type": "kind_of", "name": "name_of", "attr": "name_of", "field": "name_of",
    "func": "func_of", "value": "svalue_of", "object": "object_of", "index": "sindex_of",
    "args": "args_of",   # resync-campaign.md R1: the args LIST → `array emit_ir`
    # cf6.md M1.1: match pattern/case keys — `pattern` (KIND) / `ctor` (NAME) are strings;
    # `captures` is a reflected node list (`args_of`); `body` is an OPAQUE stmt-list
    # (`stmts_of : → array int`); `guard` is a single node (`svalue_of`).
    "pattern": "kind_of", "ctor": "name_of", "captures": "args_of",
    "body": "stmts_of", "guard": "svalue_of", "parts": "args_of", "elts": "args_of",
    "lower": "svalue_of", "upper": "svalue_of",   # 07-03-refactor R4: SliceExpr bound sub-nodes
}
# `pattern` is CONTEXT-DEPENDENT: SUBSCRIPT `c["pattern"]` → a sub-NODE (below); `.get("pattern")`
# → the KIND string (here). Different code paths read each tuple, so it appears in both.
_EMIT_IR_STR_KEYS = ("type", "name", "attr", "field", "func", "ctor", "pattern")   # via `.get`
_EMIT_IR_NODE_KEYS = ("value", "object", "index", "pattern", "guard")   # via subscript → node
# self-tcb-reduction T1.a: STRING-valued attribute reads on a base-`ExprIR` emit_ir node
# (`node.kind`/`node.var`/`node.op`/…, where the handler annotates `node: "ExprIR"` but accesses a
# concrete subclass's str field) → the discriminant/name projection. Non-listed attrs fall to the
# `svalue_of` sub-node default. @mutable_state-gated in `_handle_attribute_expr`/`_is_string_expr`.
_EMIT_IR_STR_ATTRS = {"kind": "kind_of", "var": "name_of", "op": "name_of",
                      "label": "name_of", "name": "name_of", "func": "func_of",
                      "base": "name_of", "base1": "name_of", "base2": "name_of"}
from module6_whyml.struct_format import parse_format
from module6_whyml.expr_ghost_collections import GhostCollectionOpsMixin
from module6_whyml.expr_ghost_spec_ops import GhostSpecOpsMixin


class ExpressionEmissionMixin(GhostCollectionOpsMixin, GhostSpecOpsMixin):
    """Expression-emission dispatch: every IR expression-shape `_handle_*_expr`
    handler routed via `_EXPR_DISPATCH` on the facade, plus the orchestration
    entrypoints (`_expr_to_whyml`, `_expr_to_whyml_string_ctx`) and the shared
    helpers (`_to_bool`, `_coerce_*`, `_match_pattern_cond`, ...). Mixed into
    Module6_WhyMLTranspiler. `_EXPR_DISPATCH` stays on the facade as a class
    attribute — moving it would force a circular import.
    """

    _BITWISE_FOLD_OPS = {
        "&": lambda a, b: a & b, "|": lambda a, b: a | b, "^": lambda a, b: a ^ b,
        "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b, "**": lambda a, b: a ** b,
    }
    _BITWISE_FN_NAMES = {
        "&": "bit_and", "|": "bit_or", "^": "bit_xor",
        "<<": "bit_lshift", ">>": "bit_rshift", "**": "py_pow",
    }

    def _e(self, ir: Dict, lr: Set[str]) -> str:
        """Shorthand for _expr_to_whyml within ghost handlers."""
        return self._expr_to_whyml(ir, lr)

    def _whyml_string_literal(self, s: str) -> str:
        """A Python string → its WhyML double-quoted string literal, backslash and
        double-quote escaped. Pure (`assigns \\nothing`). Extracted (07-03-refactor R5)
        from the duplicated inline escaper in `_handle_var_expr` / `_call_named_builtins`."""
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    def _to_bool(self, whyml_str: str, ir_expr: Dict[str, Any]) -> str:
        """Coerce a WhyML expression to bool if it might be int.
        Comparison operators and bool literals are already bool.
        Calls to isinstance_check, hasattr_check are already bool.
        Other expressions (int) need `<> 0` coercion."""
        t = ir_expr.get("type", "")
        op = ir_expr.get("op", "")
        # self-tcb-reduction T1.a: `if subst:` on a dict/set param (an `Optional[Dict]` modeled as
        # `map` — None ≡ empty) is the present-guard before `name in subst`; a sound over-approx
        # for the type-safety+frame contract is `true` (the `in` does the real check). @mutable_state.
        if (t == "Var"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and getattr(self, "_current_symbol_table", {}).get(ir_expr.get("name"))
                in ("dict", "set", "frozenset")):
            return "true"
        # resync-campaign.md R1: `val_ir.get("args")` lowers to `(args_of …)` : `array emit_ir`
        # — a truthiness (`if not val_ir.get("args")` = "no args") is array-emptiness, never the
        # int `<> 0` coercion. @mutable_state emit_ir reflection only.
        if whyml_str.startswith("(args_of "):
            return f"(Array.length {whyml_str} <> 0)"
        # 07-03-refactor R4: `if <emit_ir sub-node>:` (an Optional[ExprIR] field, e.g.
        # `if sl.get("lower")`) is a present-guard; the sub-node is always-present in the model, so
        # `true` is a sound over-approx for the type-safety+frame contract. @mutable_state.
        if (getattr(self, "_current_self_type", None) in getattr(self, "_mutable_state_classes", set())
                and any(whyml_str.startswith(p) for p in
                        ("(svalue_of ", "(object_of ", "(sindex_of ", "(arg0_of "))):
            return "true"
        # cf6.md M1.6: `if existing_caps:` on an emit_ir-element ARRAY LOCAL is array-emptiness.
        if (t == "Var"
                and getattr(self, "_array_elem_types", {}).get(ir_expr.get("name")) == "emit_ir"):
            return f"(Array.length ({whyml_str}) <> 0)"
        # cf6.md M1.6: `if wb.strip():` — a STRING truthiness is non-emptiness. @mutable_state.
        if (getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr(ir_expr)):
            self._add_abstract_op(
                "val str_eq_op (a b: string) : bool\n"
                "    ensures { result <-> (a = b) }")
            return f'(not (str_eq_op {whyml_str} ""))'
        # Already boolean: comparisons, not, bool literals, isinstance
        if t == "BinOp" and op in ("==", "!=", "<", ">", "<=", ">=", "in", "not in"):
            return whyml_str
        if t == "BinOp" and op in ("and", "or") and self._in_spec:
            # In spec context, and/or use && / || which are already bool
            return whyml_str
        if t == "UnaryOp" and op == "not":
            return whyml_str
        # `\old(e)` / `e @label` is boolean iff its inner expression is — recurse so
        # `\old(x < 0)` is not int-coerced (it underlies `complete`/`disjoint`).
        if t in ("Old", "At"):
            return self._to_bool(whyml_str, ir_expr.get("expr", {}))
        if t == "Bool":
            # In body context, Bool emits 1/0 but we need true/false for formulas
            if whyml_str == "1":
                return "true"
            if whyml_str == "0":
                return "false"
            return whyml_str
        if t == "Call" and ir_expr.get("func", "") in ("isinstance", "hasattr", "any", "all"):
            # `any(...)`/`all(...)` lower to the bool-returning `any_1`/`all_1` vals — a
            # truthiness `if any(...)` / `not any(...)` must use them directly, never the
            # int `(… <> 0)` coercion (bool <> int type error). No corpus driver uses
            # `any`/`all` in a truthiness position, so this is byte-identical.
            return whyml_str
        # inductive.md: a predicate application `p(args)` is already a formula (Why3
        # `predicate`), not an int — never `<> 0`-coerce it (e.g. inside `and`/`or` in a
        # reflection inversion lemma `… or (n >= 2 and even(n - 2))`).
        if t == "Call" and ir_expr.get("func", "") in getattr(self, "_inductive_preds", set()):
            return whyml_str
        if t in ("Exists", "Forall", "Compare"):
            return whyml_str
        # Ghost set/map predicates already return bool — no <> 0 needed
        if t in ("SetMem", "SetSubset", "SetEq", "MapEq", "HasKey"):
            return whyml_str
        # Array locals can't be compared with <> 0; emit true (always allocated)
        if t == "Var":
            name = ir_expr.get("name", "")
            # self-ir-schema.md IR4: a seq-promoted list local (`seq_parts = []; .append`)
            # is truthy iff non-empty — `Seq.length x <> 0` (the seq counterpart of the
            # array-length truthiness). @mutable_state path (via _seq_locals membership).
            if (name in getattr(self, "_seq_locals", set())
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return f"(Seq.length {whyml_str} <> 0)"
            if name in self._array_locals:
                return "true"
            # no-more-int emitter L4c: a list/array-typed var (`array int`, e.g. the
            # `rest: List[...]` param) is truthy iff non-empty — `Array.length x <> 0`,
            # the faithful Python list-truthiness — not the int `x <> 0` (a type error
            # on an array). Keyed on the SAME signals that lower the var to `array int`
            # (`_current_array1d_params` or a `list`/`bytes`/`bytearray` symbol type), so
            # `Array.length` is well-typed exactly when they fire. Byte-identical: a
            # corpus `if <array_var>:` would otherwise emit the ill-typed `<> 0`, so none
            # exists to change.
            if (name in getattr(self, "_current_array1d_params", set())
                    or getattr(self, "_current_symbol_table", {}).get(name)
                    in ("list", "bytes", "bytearray")
                    # self-ir-schema.md IR4 / list-comp: a comprehension-bound array local
                    # (`shared_for_mutex`) is truthy iff non-empty — recognized via the
                    # element-type map (@mutable_state; empty for the corpus).
                    or name in getattr(self, "_array_elem_types", {})):
                return f"(Array.length {whyml_str} <> 0)"
            # typed-ir-for-b-ceiling.md §13: a STRING var (`rest_code = self._stmts_
            # to_whyml(...)`) is truthy iff non-empty — `String.length s <> 0`, the
            # faithful Python str-truthiness, not the ill-typed int `s <> 0`. Keyed on
            # the same signals that lower the var to `string`; byte-identical (a corpus
            # `if <str_var>:` would otherwise emit the ill-typed `<> 0`, so none exists).
            if (name in getattr(self, "_string_local_vars", set())
                    or getattr(self, "_current_symbol_table", {}).get(name)
                    in ("str", "string")):
                if self._in_spec:
                    return f"(String.length {whyml_str} <> 0)"
                self._add_abstract_op(
                    "val str_length_op (s: string) : int\n"
                    "    ensures { result = (String.length s) }")
                return f"(str_length_op {whyml_str} <> 0)"
            # typed-ir §19: an emit_ir local (`if assume_inv:` on an `Optional[ExprIR]`)
            # is truthy iff present — modeled always-present (`true`), like the emit_ir
            # `is None` comparison; sound for the type-safety+frame contracts (both arms
            # type-check, no self-field write). Gated by the emit_ir tags.
            if (name in getattr(self, "_emit_ir_local_vars", set())
                    or self._is_emit_ir_expr(ir_expr)):
                return "true"
        # Coerce int → bool
        return f"({whyml_str} <> 0)"

    @staticmethod
    def _coerce_str_arg(whyml_str: str) -> str:
        """Convert a WhyML string literal to an int hash for abstract val arguments."""
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        return whyml_str

    def _materialize_if_seq(self, whyml_str: str, arg_ir: "ExprIR") -> str:
        """L2 (os-bodyvc-spec): if `arg_ir` is a seq-promoted local Var, bridge it seq→array with
        `materialize` so it can flow into an `array int` slot (e.g. `bytes(parts)`,
        `_write_entry(p, slot, n, parts)`). The return-arr `materialize` val is `seq int -> array int`
        (length+element preserving), emitted on demand. Non-seq args are returned unchanged."""
        if (isinstance(arg_ir, dict) and arg_ir.get("type") == "Var"
                and arg_ir.get("name") in getattr(self, "_seq_locals", set())):
            self._materialize_bridge()
            return f"(materialize {whyml_str})"
        return whyml_str

    @staticmethod
    def _array_coerce_arg(whyml_str: str) -> str:
        """Coerce an arbitrary WhyML expression to an `array int`. Used
        when abstract vals (`any_1`, `all_1`, `sorted_1`, `list_new`)
        expect an array but the actual arg is an int — typically because
        the IR dropped an unsupported iterable shape (generator
        expression, comprehension, variadic *args) to a scalar. A
        length-1 placeholder array works because the abstract vals have
        no axioms about their input contents.

        Recognises explicit array-shaped expressions and leaves them
        alone: `Array.make ...`, `Array.get ...`, `sorted_1 ...`, bare
        identifiers we can't disambiguate (passed through; callers must
        ensure their type). For everything else, returns the placeholder."""
        stripped = whyml_str.strip()
        if stripped == "0":
            return "(Array.make 1 0)"
        # Already array-shaped — leave alone.
        if (stripped.startswith("(Array.make")
                or stripped.startswith("(Array.get")
                or stripped.startswith("(sorted_1 ")
                or stripped.startswith("(list_new ")
                or stripped.startswith("(any_1 ")
                or stripped.startswith("(all_1 ")):
            return whyml_str
        # Bare identifier or a dotted FIELD access (`self.fields`) — could be array-typed (callee's
        # responsibility); pass through. (Track C / cprobe: clobbering `self.fields` to a placeholder
        # severs it from its representation invariant, so a callee's array precondition can never
        # discharge from `0 <= self.fields[k] <= MAX`.)
        if stripped.replace("_", "").replace("!", "").replace(".", "").isalnum():
            return whyml_str
        # L2 sub-gap 2 (os-bodyvc-spec): a function application `(fn arg…)` or array-literal
        # `(let _alit = …)` in an array slot is an array-returning expression (e.g. `(pack16 x)`,
        # `(materialize !s)`, the `[..]` literal). Pass it through — clobbering it to a placeholder
        # discards the value, which breaks contract-composition round-trips
        # (`unpack(pack(x)) == x` lost `pack(x)` to `(Array.make 1 0)`). Only genuinely-scalar args
        # (`0`, a numeric `(a + b)`) still get the placeholder.
        if stripped.startswith("("):
            inner = stripped[1:].lstrip()
            head = inner.split(" ", 1)[0] if " " in inner else inner.rstrip(")")
            head_ok = head.lstrip("!").replace("_", "").replace(".", "").isalnum()
            if head and head_ok and not head.lstrip("!")[:1].isdigit():
                return whyml_str
        # Anything else (BinOp result, parenthesised int expression) —
        # coerce to placeholder since we can't recover the array.
        return "(Array.make 1 0)"

    def _deref(self, expr: str) -> str:
        """Dereference a WhyML ref-typed operand: `x` → `!x` (idempotent — a leading
        `!` is normalized, not doubled). Used by the set/list/map handlers, where a
        collection operand may arrive already-dereffed."""
        return f"!{expr.lstrip('!')}" if expr.startswith("!") else expr

    def _coerce_to_int(self, whyml_str: str) -> str:
        """Coerce any non-int WhyML expression to int for abstract val arguments.

        no-more-int A6: the `self`/record → int category was retired here — a
        corpus-wide audit found it fires 0 times now that record params/locals
        are handled by the record-aware dotted-call path (A2a/A2c), so the
        `self_to_int_<type>` abstract op is dead. The remaining categories are
        not erasure of a now-typed value: `array`/`map` are defensive
        placeholders that keep a genuinely-untyped collection flow from emitting
        an ill-typed operand where `int` is expected; `tuple`→hash and the
        `string`→hash fallback are the benign documented collapses (A7)."""
        # String literals → int hash
        if whyml_str.startswith('"') and whyml_str.endswith('"'):
            return str(stable_hash(whyml_str))
        # Array-shaped expressions can't be passed where int is expected.
        # The array's contents have no axioms; coerce to 0 placeholder.
        stripped = whyml_str.strip()
        array_prefixes = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
                          "(list_new_arr ", "(any_1 ", "(all_1 ")
        for prefix in array_prefixes:
            if stripped.startswith(prefix):
                return "0"
        # Map-shaped expressions (body-set / body-dict updates) can't be
        # passed where int is expected — same placeholder.
        map_prefixes = ("(map_update_some ", "(map_update_none ",
                        "(const (None: option int)")
        for prefix in map_prefixes:
            if stripped.startswith(prefix):
                return "0"
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
        return whyml_str

    # ----- no-more-int F1: dict value-type (ν) dispatch, consolidated -----
    # A dict's value type ν ∈ {int (default), "string", "seq int", "map …"}
    # drives three emission decisions — the empty-map literal (first assignment),
    # the missing-key placeholder (subscript read), and the stored-value coercion
    # (subscript write). These were a parallel `if ν == … elif …` ladder
    # duplicated at each of the three sites; these helpers centralise that ladder.
    # Output is byte-identical to the former inline branches.

    def _dv_empty_default(self, nu: str) -> str:
        """Empty-map literal for a dict local's first assignment; `None` for an
        int dict (the caller keeps the `(const (None: option int))` it has)."""
        if nu == "string":
            return "(const (None: option string))"
        if nu == "seq int":
            return "(const (None: option (seq int)))"
        if nu and nu.startswith("map "):
            return f"(const (None: option ({nu})))"
        return ""

    def _dv_missing_default(self, nu: str) -> str:
        """`None ->` placeholder for a dict subscript read (typed per ν; proven
        dead under `#@ no_exception KeyError`, the ambient default otherwise)."""
        if nu == "string":
            return '""'
        if nu and nu.startswith("seq "):
            # #15: `Dict[str, List[T]]` value (`seq string`/`seq int`) -> the empty seq default.
            return f"(Seq.empty: {nu})"
        if nu and nu.startswith("map "):
            inner_v = (nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                       if "(option " in nu else "int")
            return f"(const (None: option {inner_v}))"
        return "0"

    def _dv_store_value(self, nu: Optional[str], val_expr: str) -> str:
        """The value stored at `d[k] = val`: a `seq int` snapshots the array
        (ownership-discipline §3), a string/nested-map value passes through
        unhashed, otherwise int-coerce."""
        if nu == "seq int":
            self._add_abstract_op(
                "val function array_to_seq (a: array int) : seq int\n"
                "    ensures { Seq.length result = Array.length a }")
            return f"(array_to_seq {self._array_coerce_arg(val_expr)})"
        if nu == "string" or (nu and nu.startswith("map ")):
            return val_expr
        return self._coerce_to_int(val_expr)

    def _match_pattern_cond(self, pat: Dict[str, Any], subject: str, local_refs: Set[str]) -> str:
        """Generate a WhyML boolean condition for a match pattern."""
        kind = pat.get("pattern", "Unknown")
        if kind == "Wildcard":
            return "true"
        elif kind == "Value":
            val = self._expr_to_whyml(pat["value"], local_refs)
            return f"({subject} = {val})"
        elif kind == "Capture":
            if pat.get("inner"):
                return self._match_pattern_cond(pat["inner"], subject, local_refs)
            return "true"
        elif kind == "Or":
            alts = [self._match_pattern_cond(a, subject, local_refs) for a in pat.get("alternatives", [])]
            return " || ".join(alts) if alts else "true"
        return "true"

    def _emit_membership(self, op: str, expr: Dict[str, Any], left: str, right: str,
                          local_refs: Set[str], invariant_ctx: bool,
                          subst: Optional[Dict[str, str]]) -> str:
        """Emit `in` / `not in` against either an inline collection literal
        (Tuple/ArrayLit/SetLit), a body-level dict (match-based, since
        Why3 program code lacks decidable equality on `option int`), or a
        generic abstract `contains_check`."""
        negate = op == "not in"
        rhs = expr.get("right", {})
        if rhs.get("type") in ("Tuple", "ArrayLit", "SetLit"):
            elts = rhs.get("elts", [])
            if elts:
                # str-list-elements: `name in ('.', '..')` with a STRING `name` is a
                # disjunction of string equalities — route each to `str_eq_op` (content
                # equality) instead of the int-hash compare, so the operands stay `string`
                # (a string `name = <int hash>` is a type error). Int operands are
                # byte-identical (the `_coerce_str_arg` int-hash path below).
                left_is_str = self._is_string_expr(left_ir) if (left_ir := expr.get("left")) else False
                if not self._in_spec and left_is_str:
                    self._add_abstract_op(
                        "val str_eq_op (a: string) (b: string) : bool\n"
                        "    ensures { result <-> (a = b) }")
                    checks = []
                    for elt in elts:
                        elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                        checks.append(f"(str_eq_op {left} {elt_w})")
                    joined = f"({' || '.join(checks)})"
                    return f"(not {joined})" if negate else joined
                left_c = self._coerce_str_arg(left)
                checks = []
                for elt in elts:
                    elt_w = self._expr_to_whyml(elt, local_refs, invariant_ctx, subst)
                    checks.append(f"({left_c} = {self._coerce_str_arg(elt_w)})")
                joined = f"({' || '.join(checks)})"
                return f"(not {joined})" if negate else joined
        # Body-local dict OR set/dict-typed parameter OR self.<dict-field>
        rhs_is_map = False
        if rhs.get("type") == "Var":
            rname = rhs.get("name", "")
            if rname in self._dict_locals:
                rhs_is_map = True
            elif self._current_symbol_table.get(rname) in ("set", "dict", "frozenset"):
                rhs_is_map = True
            else:
                # §26: `k in X` where X aliases a self dict-field → membership on
                # `self.<field>` (the getattr-bound-local form of `k in self.<field>`).
                _alias = self._alias_self_field(rname)
                if _alias:
                    rhs_is_map = True
                    right = f"self.{self._field_label(getattr(self, '_current_self_type', None), _alias.split('.', 1)[1])}"
        if not rhs_is_map and rhs.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(rhs)
            if ft in ("set", "dict", "frozenset"):
                rhs_is_map = True
        # typed-ir §15 (getattr) + faithful-string-op tail: `x in getattr(self, "<field>",
        # set())` on a `set`/`dict` self-field — the defensive-read form of `x in
        # self.<field>`. Rewrite `right` to the real `self.<field>` map so the string-key
        # `str_hash_op` membership below fires (was falling to opaque `contains_check`).
        if not rhs_is_map and rhs.get("type") == "Call":
            _gf = self._getattr_self_field(rhs)
            # self-tcb-reduction T1.a: also fire for a SET self-field (`getattr(self, "_seq_locals",
            # set())`), not only dict fields — mirrors the direct `x in self._set_field` path so the
            # string key gets `str_hash_op`-hashed instead of the opaque `contains_check`.
            _gf_coll = _gf and (
                self._self_field_dict_nu(f"self.{_gf}") is not None
                or self._field_type_of({"type": "Attribute",
                                        "object": {"type": "Var", "name": "self"},
                                        "attr": _gf}) in ("set", "dict", "frozenset"))
            if _gf_coll:
                rhs_is_map = True
                # the direct `self.<label>` field access (matching the non-getattr
                # `x in self._seq_locals` form), NOT a synthetic Attribute IR — which
                # lowers to the opaque `get_<field>` accessor.
                right = f"self.{self._field_label(getattr(self, '_current_self_type', None), _gf)}"
        # self-tcb-reduction T1.a: `x in self._method()` where the method returns a
        # `Set[str]`/`dict` (`name in self._module_binding_names()`) → map membership (the RHS
        # `right` is already the abstract-val call returning the map). @mutable_state.
        if not rhs_is_map and rhs.get("type") == "Call" and not self._getattr_self_field(rhs):
            _fn = rhs.get("func", "")
            if isinstance(_fn, str) and _fn.startswith("self."):
                _cls = getattr(self, "_current_self_type", None)
                _key = f"{_cls}__{_fn[len('self.'):]}" if _cls else _fn
                if getattr(self, "_module_method_return_types", {}).get(_key) in (
                        "map int (option int)", "set", "dict", "frozenset"):
                    rhs_is_map = True
        # nested-map.md: `k in self._nested_dict.get(k1, {})` — `.get` on a NESTED-dict field
        # returns the INNER map (its value_type is `map …`), so membership hashes the key into
        # it. The lowered `right` is already the inner-map match-expr. @mutable_state.
        if not rhs_is_map and rhs.get("type") == "Call":
            _fn = rhs.get("func", "")
            if isinstance(_fn, str) and _fn.endswith(".get"):
                _recv = _fn[:-len(".get")]
                _nu = self._self_field_dict_nu(_recv) if _recv.startswith("self.") else None
                if isinstance(_nu, str) and _nu.startswith(("map ", "seq ", "array ")):
                    rhs_is_map = True
        if rhs_is_map:
            # todict-reflection-plan.md R3: a STRING key into a `Set[str]`/`dict[str,_]`
            # (an int-keyed map) is hashed with `str_hash_op` — the read-side analogue of
            # the M.7 `.add` write (`self.f <- map_update_some … (str_hash_op k) …`), so
            # `field in self._all_record_fields` typechecks. Fires only when the key is a
            # string expr (an int key keeps the `_coerce_to_int` path) → byte-identical.
            # A STRING key into an int-keyed map (a `Set[str]` field, OR a body dict
            # `map _ (option int)`) is `str_hash_op`-hashed — the read-side analogue of the
            # M.7 `.add`. The subscript `d[k]` hashes the same way (`_lower_dict_get_call`),
            # so membership and subscript agree on the key type. Byte-identical (an int key
            # keeps `_coerce_to_int`). typed-ir-for-b-ceiling.md §9.
            _left_ir = expr.get("left", {})
            _str_keyed_lit = getattr(self, "_dict_key_types", {}).get(
                rhs.get("name", "") if rhs.get("type") == "Var" else "") == "string"
            if _str_keyed_lit:
                # cleared-hash.md S3: the receiver map is `map string (option ν)`
                # (κ = string), so membership reads the RAW string key — native
                # `String.(=)`, no hash. `_coerce_to_int` would hash a string
                # LITERAL to an int (`stable_hash`), an int operand against a
                # `map string` map (a type error) and the very collision-opacity
                # this migration removes. A `str`-typed variable key passes
                # through `left` unchanged.
                left_c = left
            elif not self._in_spec and self._is_string_expr(_left_ir):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                left_c = f"(str_hash_op {left})"
            else:
                left_c = self._coerce_to_int(left)
            arms = ("| Some _ -> false | None -> true" if negate
                    else "| Some _ -> true | None -> false")
            return f"(match Map.get ({right}) ({left_c}) with {arms} end)"
        # strings-plan Stage 2: `needle in haystack` for strings is substring containment, an
        # uninterpreted bool op over string operands (content witness deferred — see plan).
        if self._is_string_expr(rhs):
            # strings-plan Stage 4: the containment witness. `needle in haystack` holds iff
            # `needle` occurs as a contiguous substring at some position.
            # 07-0647-spec R10/S2.1: in SPEC context (requires/ensures) the op must be a
            # LOGIC term — a program `val` is illegal in a formula ("unbound symbol"). Emit
            # the existential directly (pure `string.String` logic, already imported). In a
            # body the `val str_contains_op` (uninterpreted bool) is used.
            if self._in_spec:
                form = (f"(exists _si: int. 0 <= _si /\\ "
                        f"_si + String.length {left} <= String.length {right} /\\ "
                        f"String.substring {right} _si (String.length {left}) = {left})")
                return f"(not {form})" if negate else form
            self._add_abstract_op(
                "val str_contains_op (haystack: string) (needle: string) : bool\n"
                "    ensures { result <->\n"
                "      (exists i: int. 0 <= i /\\\n"
                "        i + String.length needle <= String.length haystack /\\\n"
                "        String.substring haystack i (String.length needle) = needle) }")
            scall = f"(str_contains_op {right} {left})"
            return f"(not {scall})" if negate else scall
        self._add_abstract_op("val contains_check (x: int) (c: int) : bool")
        call = f"(contains_check {self._coerce_str_arg(left)} {self._coerce_str_arg(right)})"
        return f"(not {call})" if negate else call

    def _emit_bitwise_or_power(self, op_char: str, expr: Dict[str, Any],
                                left: str, right: str) -> str:
        """Emit `&`/`|`/`^`/`<<`/`>>`/`**`. Constant-fold when both
        operands are literal ints; otherwise emit an abstract val call.
        Coerce array- or map-shaped operands to int (the abstract val is
        `int -> int -> int`) — Python `set | set` (treated by Module6 as
        bitwise on int) and similar shape-confused cases land here."""
        left_ir = expr.get("left", {})
        right_ir = expr.get("right", {})
        if (left_ir.get("type") == "Number" and right_ir.get("type") == "Number"
                and isinstance(left_ir.get("value"), int)
                and isinstance(right_ir.get("value"), int)):
            try:
                return str(self._BITWISE_FOLD_OPS[op_char](left_ir["value"], right_ir["value"]))
            except (ValueError, OverflowError):
                pass
        op_fn = self._BITWISE_FN_NAMES[op_char]
        # `val function` (Why3 idiom for "pure program + logic symbol"):
        # bit_and / bit_or / bit_xor / bit_lshift / bit_rshift / py_pow
        # are pure mathematical operations on int. `val function`
        # declares both a program-callable and a logical symbol, so
        # the body can call them AND `#@ proof rocq` axioms can
        # constrain them (axioms can only reference logical symbols).
        self._add_abstract_op(f"val function {op_fn} (x: int) (y: int) : int")
        return f"({op_fn} {self._coerce_to_int(left)} {self._coerce_to_int(right)})"

    # typed-ir-for-b-ceiling.md B-C1: the inline `{"type": K, …}` node kinds this
    # lowers to `exprir` constructors, and the payload field each constructor reads.
    _IRNODE_CTORS = {
        "Var":      ("IrVar", ["name"]),
        "Attribute": ("IrAttr", ["object", "attr"]),
        "String":   ("IrStr", ["value"]),
        "Number":   ("IrNum", ["value"]),
        "RawWhyml": ("IrRaw", ["whyml"]),
    }

    def _is_emit_ir_expr(self, ir: Any) -> bool:
        """typed-ir-for-b-ceiling.md B-C2: True if `ir` lowers to the `emit_ir` sum — an
        inline `{"type": K}` construction, an ExprIR-valued record field read
        (`stmt.upper`), or an ExprIR-typed Var (param/local). Used to type `x is None`
        and other emit_ir-vs-int decisions. Gated by the ExprIR annotation tags."""
        if not isinstance(ir, dict):
            return False
        t = ir.get("type")
        if t == "DictLit":
            for k in ir.get("keys", []):
                if isinstance(k, dict) and k.get("type") == "String" and k.get("value") == "type":
                    return True
            return False
        if t in ("Attribute", "FieldGet"):
            obj = ir.get("object", {})
            if isinstance(obj, dict) and obj.get("type") == "Var":
                rec = getattr(self, "_current_symbol_table", {}).get(obj.get("name", ""))
                rt = getattr(self, "_record_types", {}).get(rec)
                if rt:
                    # cf6.md M1.5: a field carrying a `value_type` (element type) is a COLLECTION
                    # (`List[ExprIR]` → `array emit_ir`), NOT a scalar node — `_irnode_ann_name`
                    # mis-tags `List[ExprIR]` as scalar `"ExprIR"`, so guard on the collection
                    # marker. A scalar `value: ExprIR` field has no value_type → still matched.
                    if ir.get("attr", "") in rt.get("field_value_types", {}):
                        return False
                    ft = rt.get("field_types", {}).get(ir.get("attr", ""))
                    return ft in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "emit_ir")
            # self-ir-schema.md IR2: `<emit_ir>.value` / `.target` (a StmtIR field access on
            # an emit_ir node, e.g. `body_stmts[-1].value`) is itself an emit_ir sub-node.
            # self-tcb-reduction T1.a: EXCLUDE node-LIST attrs (`.elts`/`.parts`/…) — those are
            # `array emit_ir` (`args_of`), NOT a scalar node, so they are collected as array locals.
            if ((ir.get("attr") or ir.get("field")) not in ("elts", "parts", "args", "captures")
                    and isinstance(obj, dict) and self._is_emit_ir_expr(obj)
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return True
            return False
        if t == "Var":
            if ir.get("name", "") in getattr(self, "_todict_aliases", {}):
                return True   # `arr = stmt.array.to_dict()` aliases an emit_ir node
            return getattr(self, "_current_symbol_table", {}).get(ir.get("name", "")) in (
                "ExprIR", "StmtIR", "IRNode", "ContractExprIR")
        # B-C5: an args-list ELEMENT `<emit_ir Call>.args[i]` / `(… or [{}])[i]` is an
        # emit_ir sub-node (arg0_of), so a local bound from it types as emit_ir (§19).
        if t in ("Subscript", "SliceAccess"):
            if self._emit_ir_args_recv_ir(ir.get("value", {})) is not None:
                return True
            if self._emit_ir_args_recv_ir(ir.get("value", {}), "elts") is not None:
                return True
            # self-ir-schema.md IR2 / seq-model-pivot.md SQ3: an element of an `array emit_ir`
            # OR `seq emit_ir` local (`body_stmts[-1]`) is an emit_ir node.
            _vv = ir.get("value", {})
            if (isinstance(_vv, dict) and _vv.get("type") == "Var"
                    and (getattr(self, "_array_elem_types", {}).get(_vv.get("name")) == "emit_ir"
                         or getattr(self, "_seq_value_types", {}).get(_vv.get("name")) == "emit_ir")):
                return True
            # §26: a projection-key subscript `<emit_ir>["value"/"object"/"index"]`
            # is an emit_ir sub-node (chaining, e.g. `arr["value"]["name"]`).
            # self-tcb-reduction T1.a: EXCLUDE subscript "object" — `expr['object']` is the object
            # NAME string (`name_of ∘ object_of`), not a sub-node (see `_handle_subscript`).
            _kir = ir.get("index", {})
            if (isinstance(_kir, dict) and _kir.get("type") == "String"
                    and _kir.get("value") in _EMIT_IR_NODE_KEYS and _kir.get("value") != "object"
                    and self._is_emit_ir_expr(ir.get("value", {}))):
                return True
        # item34.md CF1: `<x>.to_dict()` (no args) is an emit_ir node (to_dict is identity on
        # the typed IR) in a @mutable_state module.
        if (t == "Call" and isinstance(ir.get("func"), str)
                and ir["func"].endswith(".to_dict") and not ir.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            return True
        # §26: a `.get("value"/"object"/"index")` on an emit_ir receiver is an emit_ir
        # sub-node (nested `.get` chaining, e.g. `arr.get("value").get("type")`).
        if t == "Call":
            _fn = ir.get("func")
            if isinstance(_fn, str) and _fn.endswith(".get"):
                _a = ir.get("args") or []
                if (len(_a) >= 1 and isinstance(_a[0], dict)
                        and _a[0].get("type") == "String"
                        and _a[0].get("value") in _EMIT_IR_NODE_KEYS
                        and self._is_emit_ir_expr({"type": "Var", "name": _fn[:-len(".get")]})):
                    return True
        return False

    def _todict_recv_node_ir(self, recv_dotted: str) -> Dict[str, Any]:
        """The node IR for a dotted receiver (`self.types` → `Attribute(Var(self), types)`)."""
        parts = recv_dotted.split(".")
        node: Dict[str, Any] = {"type": "Var", "name": parts[0]}
        for p in parts[1:]:
            node = {"type": "Attribute", "object": node, "attr": p}
        return node

    @staticmethod
    def _getattr_self_field(recv: "ExprIR") -> str:
        """typed-ir-for-b-ceiling.md §14: if `recv` is `getattr(self, "<field>", …)`
        (a defensive self-field access) return the string `<field>`, else None."""
        if not (isinstance(recv, dict) and recv.get("type") == "Call"
                and recv.get("func") == "getattr"):
            return ""
        a = recv.get("args", [])
        if (len(a) >= 2 and isinstance(a[0], dict) and a[0].get("name") == "self"
                and isinstance(a[1], dict) and a[1].get("type") == "String"):
            return a[1].get("value")
        return ""

    def _alias_self_field(self, name: str) -> str:
        """§26: if `name` is a local bound from `getattr(self, "<field>", …)` on a
        dict/set self-field, return the dotted `self.<field>`; else None."""
        fld = getattr(self, "_getattr_self_dict_aliases", {}).get(name)
        return f"self.{fld}" if fld else ""

    def _iter_elem_class(self, iter_ir: "ExprIR") -> str:
        """self-ir-schema.md IR2: the record class of a comprehension iterable's ELEMENTS,
        for typing the loop var during element-type inference. `self.ir.get("shared_vars")`
        → "sharedvar"; None otherwise (the loop var stays untyped)."""
        if (isinstance(iter_ir, dict) and iter_ir.get("type") == "Call"
                and iter_ir.get("func") == "self.ir.get"):
            _a = iter_ir.get("args") or []
            if (_a and isinstance(_a[0], dict) and _a[0].get("type") == "String"
                    and _a[0].get("value") == "shared_vars"):
                return "sharedvar"
        # item34.md CF5: iterating a `string`-element name-collection (`for e in body_raised`,
        # `for tag in candidates`) binds the loop var to a `string` — so `handler_catches(base,
        # e)`/`whyml_ident(var)` type-check. Covers both the array-elem and seq-value maps.
        if (isinstance(iter_ir, dict) and iter_ir.get("type") == "Var"
                and (getattr(self, "_array_elem_types", {}).get(iter_ir.get("name")) == "string"
                     or getattr(self, "_seq_value_types", {}).get(iter_ir.get("name")) == "string")):
            return "str"
        return ""

    def _todict_emit_ir_projection(self, recv_dotted, key, local_refs, invariant_ctx, subst):
        node = self._todict_recv_node_ir(recv_dotted)
        if not self._is_emit_ir_expr(node): return None
        # B-C5: "func" projects to `func_of` (string); "value"/"index" to `svalue_of`/
        # `sindex_of` (emit_ir SUB-NODES — the reflecting handlers always pass them to
        # `_expr_to_whyml` or reflect further, never use them as a string).
        proj = _EMIT_IR_PROJ.get(key)
        if proj is None: return None
        return f"({proj} {self._expr_to_whyml(node, local_refs or set(), invariant_ctx, subst)})"

    def _emit_ir_args_recv_ir(self, arg_ir, key="args"):
        """B-C5: if `arg_ir` reads the "args" list of an emit_ir Call node — either the
        `<emit_ir>.get("args")` (Call) form OR the `<emit_ir>["args"]` (Subscript) form —
        return the receiver's emit_ir IR node, so `len(...)` lowers to `nargs_of` and
        `...[0]` to `arg0_of`. None otherwise.

        B-C6: `key` generalises this to any list-valued reflection key; `key="elts"`
        recognises a MkTuple node's `elts` list (routed to `elt{i}_of` by the caller)."""
        if not isinstance(arg_ir, dict):
            return None
        t = arg_ir.get("type")
        node = None
        # unwrap the defensive default `(<emit_ir>.get("args") or [{}])` — arg0_of already
        # returns IrOther "" for a non-Call, so the explicit `or <default>` is subsumed.
        if t == "BoolOp" and arg_ir.get("op") == "or":
            _vs = arg_ir.get("values", [])
            return self._emit_ir_args_recv_ir(_vs[0], key) if _vs else None
        if t == "BinOp" and arg_ir.get("op") == "or":
            return self._emit_ir_args_recv_ir(arg_ir.get("left", {}), key)
        if t == "Call":
            fn = arg_ir.get("func")
            if not (isinstance(fn, str) and fn.endswith(".get")):
                return None
            kir = (arg_ir.get("args") or [{}])[0]
            if not (isinstance(kir, dict) and kir.get("type") == "String"
                    and kir.get("value") == key):
                return None
            recv = fn[:-len(".get")]
            dotted = getattr(self, "_todict_aliases", {}).get(recv)
            node = (self._todict_recv_node_ir(dotted) if dotted
                    else {"type": "Var", "name": recv})
        elif t in ("Subscript", "SliceAccess"):
            kir = arg_ir.get("index", {})
            if not (isinstance(kir, dict) and kir.get("type") == "String"
                    and kir.get("value") == key):
                return None
            v = arg_ir.get("value", {})
            if isinstance(v, dict) and v.get("type") == "Var":
                dotted = getattr(self, "_todict_aliases", {}).get(v.get("name"))
                node = self._todict_recv_node_ir(dotted) if dotted else v
            else:
                node = v
        if node is None:
            return None
        return node if self._is_emit_ir_expr(node) else None

    def _str_method_recv_and_tail(self, expr):
        """faithful-string-op.md §4: for a string-method call `recv.tail(args)`, return
        (receiver_ir, tail). Computed receiver → `expr['receiver']`; dotted simple-var
        form (`s.replace`, `func.rsplit`) → a Var IR for the part before the last '.'.
        A dotted MULTI-part receiver (`self.x.replace`) returns (None, None) — it falls
        through to the opaque path (no regression) rather than mis-reconstructing."""
        fn = expr.get("func", "")
        if expr.get("receiver") is not None:
            return expr["receiver"], fn
        if isinstance(fn, str) and "." in fn:
            recv, tail = fn.rsplit(".", 1)
            if "." not in recv:
                return {"type": "Var", "name": recv}, tail
        return None, None

    def _split_call_recv_sep(self, call_ir):
        """faithful-string-op.md §3.4: if `call_ir` is `<string>.split(sep)` or
        `<string>.rsplit(sep, k)`, return (receiver_ir, sep_ir) [sep_ir may be None for a
        no-arg split]; else None. Used to lower `<split>[i]` to `str_split_elem_op`."""
        if not isinstance(call_ir, dict) or call_ir.get("type") != "Call":
            return None
        recv_ir, tail = self._str_method_recv_and_tail(call_ir)
        if tail not in ("split", "rsplit") or recv_ir is None:
            return None
        if not self._is_string_expr(recv_ir):
            return None
        return recv_ir, (call_ir.get("args") or [None])[0]

    def _is_literal_string_join(self, ir):
        """faithful-string-op.md §3.5: True if `ir` is `sep.join([s0, s1, …])` over a
        LITERAL list/tuple of STRING elements (receiver form) — the case
        `_handle_join_call` lowers to nested `str_concat_op` (a `string`)."""
        if not isinstance(ir, dict) or ir.get("type") != "Call":
            return False
        if ir.get("func") != "join" or ir.get("receiver") is None:
            return False
        a = (ir.get("args") or [{}])[0]
        if not isinstance(a, dict) or a.get("type") not in ("ArrayLit", "ListLit", "Tuple"):
            return False
        elts = a.get("elts", [])
        return bool(elts) and all(self._is_string_expr(e) for e in elts)

    _STR_VALUE_METHODS = ("replace", "lower", "upper", "strip", "lstrip", "rstrip")

    def _is_str_value_method(self, expr):
        """True if `expr` is a faithful string-VALUED method call on a string receiver
        (§3.1–3.3). Shared by `_is_string_expr` (typing) and `_handle_string_value_method`
        (lowering) so the two never disagree."""
        if not isinstance(expr, dict) or expr.get("type") != "Call":
            return False
        recv_ir, tail = self._str_method_recv_and_tail(expr)
        if tail not in self._STR_VALUE_METHODS or recv_ir is None:
            return False
        return self._is_string_expr(recv_ir)

    def _handle_string_value_method(self, expr, args, local_refs, invariant_ctx, subst):
        """faithful-string-op.md §3.1–3.3: lower `.replace`/`.lower`/`.upper`/`.strip`/
        `.lstrip`/`.rstrip` on a string receiver to a faithful `string`-typed abstract op
        with the STRONGEST SOUND length law (never over-claiming — the str_repr_op
        discipline). None if not applicable."""
        if not self._is_str_value_method(expr):
            return None
        recv_ir, tail = self._str_method_recv_and_tail(expr)
        recv = self._expr_to_whyml(recv_ir, local_refs or set(), invariant_ctx, subst)
        if tail == "replace" and len(args) == 2:
            # §3.1: char-for-char (len old = len new) preserves length; general replace
            # may grow/shrink, so no unconditional length law is sound.
            # NB `old`/`new` are Why3 reserved keywords → params named `pat`/`rep`.
            self._add_abstract_op(
                "val str_replace_op (s pat rep: string) : string\n"
                "    ensures { String.length pat = String.length rep"
                " -> String.length result = String.length s }")
            return f"(str_replace_op {recv} {args[0]} {args[1]})"
        if tail in ("lower", "upper") and len(args) == 0:
            # §3.2: case folding is NOT length-preserving in Unicode ("ß".upper()=="SS"),
            # so ONLY the non-emptiness lower bound is sound — a length-equality law
            # would be unsound.
            self._add_abstract_op(
                "val str_case_op (s: string) : string\n"
                "    ensures { String.length s >= 1 -> String.length result >= 1 }")
            return f"(str_case_op {recv})"
        if tail in ("strip", "lstrip", "rstrip") and len(args) <= 1:
            # §3.3: stripping only removes chars → result no longer than the input.
            self._add_abstract_op(
                "val str_strip_op (s: string) : string\n"
                "    ensures { String.length result <= String.length s }")
            return f"(str_strip_op {recv})"
        return None

    def _self_field_dict_nu(self, recv: str):
        """self-field-dict-reflection (typed-ir-for-b-ceiling.md §12): when `recv` is a
        `self.<field>` (or `<recordvar>.<field>`) naming a `dict`/`set`/`frozenset`
        record field, return the field's WhyML VALUE type ("string" for `dict[str, str]`,
        else "int"); None otherwise. Lets `self.<dict-field>.get(k)` read the real map."""
        if "." not in recv:
            return None
        obj, field = recv.rsplit(".", 1)
        rt_name = (self._current_self_type if obj == "self"
                   else getattr(self, "_current_record_var_classes", {}).get(obj))
        if not rt_name:
            return None
        rts = getattr(self, "_record_types", {})
        rt = (rts.get(rt_name) or rts.get(str(rt_name).lower())
              or next((v for k, v in rts.items() if k.lower() == str(rt_name).lower()), None))
        if not rt:
            return None
        ft = rt.get("field_types", {}).get(field)
        if ft not in ("dict", "set", "frozenset"):
            return None
        return rt.get("field_value_types", {}).get(field, "int")

    def _lower_irnode_construction(self, expr: Dict[str, Any], local_refs: Set[str],
                                   invariant_ctx: bool,
                                   subst: Optional[Dict[str, str]]) -> Optional[str]:
        """typed-ir-for-b-ceiling.md B-C1: lower an inline IR-node dict literal
        `{"type": "Var", "name": e}` to the typed `exprir` constructor `(EVar <e>)`.
        A `"type"` key with a STRING-literal value names the kind; the remaining keys
        supply the constructor payload. A kind we don't model, or a construction
        missing a payload field, becomes `(EOther "<kind>")` — sound: reflection then
        yields the tag and `""`, never a false value. Gated on @mutable_state (the
        emitter model); returns None (→ the caller's map fallback) otherwise."""
        if getattr(self, "_current_self_type", None) not in getattr(
                self, "_mutable_state_classes", set()):
            return None
        keys = expr.get("keys", [])
        values = expr.get("values", [])
        if not keys or len(keys) != len(values):
            return None
        fields: Dict[str, Any] = {}
        for k, v in zip(keys, values):
            if not (isinstance(k, dict) and k.get("type") == "String"):
                return None
            fields[k.get("value")] = v
        kind_ir = fields.get("type")
        if not (isinstance(kind_ir, dict) and kind_ir.get("type") == "String"):
            return None
        kind = kind_ir.get("value")
        ctor = self._IRNODE_CTORS.get(kind)
        if ctor is None:
            return f'(IrOther "{kind}")'
        cname, payload = ctor
        args = []
        for f in payload:
            if f not in fields:
                return f'(IrOther "{kind}")'
            args.append(self._expr_to_whyml(fields[f], local_refs, invariant_ctx, subst))
        return f"({cname} {' '.join(args)})"

    def _todict_routed_ir(self, recv_dotted: str, key: str) -> Dict[str, Any]:
        """todict-reflection-plan.md R1: the TYPED-field IR that `<recv>.get(key)`
        routes to, where `recv` aliases `<node>.to_dict()`. The literal key `"type"`
        → the node's `kind` tag; any other key → the same-named field. `recv_dotted`
        may be dotted (`stmt.array`) → a nested receiver."""
        field = "kind" if key == "type" else key
        parts = recv_dotted.split(".")
        node: Dict[str, Any] = {"type": "Var", "name": parts[0]}
        for p in parts[1:]:
            node = {"type": "Attribute", "object": node, "attr": p}
        return {"type": "Attribute", "object": node, "attr": field}

    def _is_string_expr(self, ir: Dict[str, Any]) -> bool:
        """True if an IR expression is string-typed: a literal, a string-producing op, or a
        `str`-typed variable. (strings-plan Stage 2 — used to route `+` to `concat`.)"""
        t = ir.get("type")
        # resync-campaign.md R2: a ternary whose BOTH arms are string-typed is string (the
        # emitter's `(if _poly then "<decl A>" else "<decl B>") + "…ensures…"` concat). Both
        # arms must be string; @mutable_state (the emitter's string decls).
        if (t == "IfExpr"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr(ir.get("body", {}))
                and self._is_string_expr(ir.get("orelse", {}))):
            return True
        # resync-campaign.md R2: `<str> or <str>` (`<get> or ""`) is string — so a `.lower()`
        # on it type-checks. @mutable_state.
        if (t == "BinOp" and ir.get("op") == "or"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr(ir.get("left", {}))
                and (self._is_string_expr(ir.get("right", {}))
                     or (isinstance(ir.get("right"), dict)
                         and ir["right"].get("type") == "None"))):
            return True
        if t == "Call":
            _fn = ir.get("func", "")
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
                    if (isinstance(_gk, dict) and _gk.get("type") == "String"
                            and _gk.get("value") in _EMIT_IR_STR_KEYS + ("value",)):
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

    def _is_float_expr(self, ir: Dict[str, Any]) -> bool:
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

    def _str_operand_to_int(self, whyml_str: str) -> str:
        """Map a string operand into the legacy int-hash domain. Used when a string is
        compared against a genuine int (e.g. an opaque `.decode()` result that PyCSL has no
        string model for): the comparison reverts to the pre-strings opaque int-equality
        rather than forcing a type-incorrect `str_eq_op`. A literal hashes directly; a
        non-literal string goes through an uninterpreted `str_hash_op`."""
        s = whyml_str.strip()
        if s.startswith('"') and s.endswith('"'):
            return str(stable_hash(whyml_str))
        self._add_abstract_op("val str_hash_op (s: string) : int")
        return f"(str_hash_op {whyml_str})"

    def _handle_binop(self, node: "ExprIR", local_refs: Set[str],
                      invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        # Phase-B-expr: typed signature. The body's deep, branchy child inspection
        # stays dict-based via the node's canonical dict view (byte-identical); the
        # handler does not read attribution keys, so the opaque-coerced node's
        # to_dict() is faithful for its purposes.
        expr = node.to_dict()
        raw_op = expr["op"]
        # [default] * size → Array.make size default
        if raw_op == "*" and expr["left"].get("type") == "ArrayLit":
            elts = expr["left"].get("elts", [])
            default_val = self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst) if elts else "0"
            size = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
            return f"(Array.make {size} {default_val})"
        # item34.md CF5: `[a] + [comp]` name-list concat (`[base] + [tag for … in body_raised
        # …]`) → `seq string`. Each arm is seq-ified via `_seq_operand` (an ArrayLit singleton
        # `snapshot`s; a comprehension over a seq is `list_comp_seq`), so the whole flow is
        # uniformly seq. @mutable_state; LEFT is a list literal / comprehension.
        if (raw_op == "+" and isinstance(expr.get("left"), dict)
                and expr["left"].get("type") in ("ArrayLit", "ListLit", "ListComp")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _l = self._seq_operand(expr["left"], local_refs or set())
            _r = self._seq_operand(expr["right"], local_refs or set())
            self._add_abstract_op(
                "val array_concat (a b: seq string) : seq string\n"
                "    ensures { Seq.length result = Seq.length a + Seq.length b }")
            return f"(array_concat {_l} {_r})"
        left = self._expr_to_whyml(expr["left"], local_refs, invariant_ctx, subst)
        right = self._expr_to_whyml(expr["right"], local_refs, invariant_ctx, subst)
        # bool-as-int convention: PyCSL int-encodes bool (a `-> bool` function returns 0/1,
        # its contract reads `\result == 0 or 1`). So a Bool literal in `==`/`!=` is INT
        # equality (Python `True == 1`, `False == 0`) — emit it as 1/0 even in spec context,
        # else `\result == True` lowers to `result = true` (bool) which mismatches the int
        # `\result` ("term has type int, expected bool"). Fixes the formal-test idiom
        # `#@ ensures \result == True`.
        if raw_op in ("==", "!="):
            if expr["left"].get("type") == "Bool":
                left = "1" if expr["left"].get("value") else "0"
            if expr["right"].get("type") == "Bool":
                right = "1" if expr["right"].get("value") else "0"
        # typing-engagement ty1 / 25-1700-typing-spec-1 §1.2 C5: `x is None`
        # (BinOp `==`/`!=` with `None`) on a Union-typed variable lowers to a
        # constructor check against the nullary `Arm_<idx>_None` ctor, NOT `x=0`.
        if raw_op in ("==", "!=") and (
                expr["left"].get("type") == "None" or
                expr["right"].get("type") == "None"):
            union_ctor = self._union_none_ctor_for(expr["left"]) or \
                self._union_none_ctor_for(expr["right"])
            if union_ctor is not None:
                var_side = expr["right"] if expr["left"].get("type") == "None" \
                    else expr["left"]
                var_str = self._expr_to_whyml(var_side, local_refs,
                                              invariant_ctx, subst)
                chk = f"({var_str} = {union_ctor})"
                return chk if raw_op == "==" else f"(not {chk})"
            # typed-ir-for-b-ceiling.md B-C2: `x is None` on an `emit_ir`-typed operand
            # (an `Optional[ExprIR]` field, e.g. `stmt.upper`) can't lower to `x = 0`
            # (emit_ir <> int). We model the optional as always-present — `is None` →
            # `false`, `is not None` → `true` — a SOUND simplification for the
            # type-safety+frame contracts we prove here (both `if` arms still type-check;
            # the arms write only locals, never self-fields, so the frame holds in both).
            # The faithful `option emit_ir` (a real `Some/None` match) is the follow-on
            # when a value-faithful `ensures` over an optional sub-node is needed. §9.
            _nn = expr["right"] if expr["left"].get("type") == "None" else expr["left"]
            if self._is_emit_ir_expr(_nn):
                return "false" if raw_op == "==" else "true"
            # cf6.md M1.6: `<tuple-local> is None` — a tuple value (`union_info =
            # self._match_subject_union_info(…)`) is always present in this model, so `is None`
            # → false / `is not None` → true (sound always-present; both `if` arms type-check).
            if (isinstance(_nn, dict) and _nn.get("type") == "Var"
                    and _nn.get("name") in getattr(self, "_ghost_tuple_vars", {})):
                return "false" if raw_op == "==" else "true"
            # i-feel-good.md I-B: `x is None`/`is not None` on a string-typed operand — an
            # `Optional[str]` local (the emitter's `self_field_name = None; … = <str>`).
            # Same sound always-present model (empty-string "" is the absent sentinel; both
            # `if` arms type-check). @mutable_state-gated → byte-identical elsewhere.
            if (self._is_string_expr(_nn)
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                return "false" if raw_op == "==" else "true"
        op = op_translate(raw_op)
        # no-more-int Stage D: float arithmetic/comparison is over Why3 `real` (RealInfix
        # `+.`/`-.`/`*.`/`/.`/`<.`/…), not int. Both operands must be float; a mixed float/int
        # binop is out of scope (documented). Arithmetic in a body bridges through an abstract
        # `val` (the real ops are logic symbols); comparisons return bool and emit directly.
        _lf = self._is_float_expr(expr["left"])
        _rf = self._is_float_expr(expr["right"])
        if _lf or _rf:
            _FARITH = {"+": ("+.", "add"), "-": ("-.", "sub"),
                       "*": ("*.", "mul"), "/": ("/.", "div")}
            if raw_op in _FARITH and _lf and _rf:  # arithmetic: both operands float
                rop, nm = _FARITH[raw_op]
                if self._in_spec:
                    return f"({left} {rop} {right})"
                self._add_abstract_op(
                    f"val float_{nm}_op (a b: real) : real\n"
                    f"    ensures {{ result = (a {rop} b) }}")
                return f"(float_{nm}_op {left} {right})"
            # comparison/equality: either operand float (the other is `\result` or a real)
            _FCMP = {"<": "<.", "<=": "<=.", ">": ">.", ">=": ">=."}
            if raw_op in _FCMP:
                return f"({left} {_FCMP[raw_op]} {right})"
            if raw_op in ("==", "!="):
                eq = f"({left} = {right})"
                return eq if raw_op == "==" else f"(not {eq})"
        # G2 strings: lexicographic comparison `< <= > >=` on two strings. Why3's
        # `string.String` exposes the *predicates* `String.lt`/`String.le` (lexicographic
        # order). `s < t` → `str_lt_op s t` (a `val:bool` bridge tied by `ensures` to
        # `String.lt`); `s <= t` → `str_le_op`. `>`/`>=` reflect by swapping operands
        # (`s > t` ⇔ `t < s`, `s >= t` ⇔ `t <= s`). Like the Python comparison protocol the
        # body returns an int (the bool→int `if … then 1 else 0` of the float-compare path).
        # Both operands must be string-typed; a mixed str/int compare is out of scope here.
        if raw_op in ("<", "<=", ">", ">=") \
                and self._is_string_expr(expr["left"]) \
                and self._is_string_expr(expr["right"]):
            self._add_abstract_op(
                "val str_lt_op (a: string) (b: string) : bool\n"
                "    ensures { result <-> String.lt a b }")
            self._add_abstract_op(
                "val str_le_op (a: string) (b: string) : bool\n"
                "    ensures { result <-> String.le a b }")
            if raw_op == "<":
                cmp = f"(str_lt_op {left} {right})"
            elif raw_op == "<=":
                cmp = f"(str_le_op {left} {right})"
            elif raw_op == ">":
                cmp = f"(str_lt_op {right} {left})"
            else:  # ">="
                cmp = f"(str_le_op {right} {left})"
            if self._in_spec:
                return cmp
            return f"(if {cmp} then 1 else 0)"
        # G2 strings: repetition `s * n` / `n * s` on a string + int. The repeated string's
        # length is `n * String.length s` (canonicalize string-first regardless of operand
        # order — multiplication is commutative on the int factor). Bridged through a `val`
        # whose `ensures` pins only the length (the content is an opaque function of s, n).
        if raw_op == "*" and (
                (self._is_string_expr(expr["left"]) and not self._is_string_expr(expr["right"]))
                or (self._is_string_expr(expr["right"]) and not self._is_string_expr(expr["left"]))):
            if self._is_string_expr(expr["left"]):
                sstr, nstr = left, right
            else:
                sstr, nstr = right, left
            self._add_abstract_op(
                "val str_repeat_op (s: string) (n: int) : string\n"
                "    requires { n >= 0 }\n"
                "    ensures { String.length result = n * String.length s }")
            return f"(str_repeat_op {sstr} {nstr})"
        # G2 strings: `%`-formatting `s % x` produces SOME string — its content is NOT
        # modeled (faithful boundary). An honest abstract `val` pins only `length >= 0` (a
        # sound over-approximation), never the int `pycsl_mod`. Fires only for a string LHS.
        if raw_op == "%" and self._is_string_expr(expr["left"]):
            self._add_abstract_op(
                "val str_mod_op (s: string) (x: 'a) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_mod_op {left} {right})"
        # strings-plan Stage 2: `s + t` on strings is concatenation, not int addition. The
        # logic symbol `concat` is fine in a spec; in a program (body) context it is bridged
        # through an abstract `val` whose `ensures` ties the result to `concat` (same pattern
        # as `len`/`str_length_op`).
        # Both operands must be string-typed: `str + int` is not valid Python concatenation, so
        # a mixed `+` is left as int addition (legacy hash model).
        if raw_op == "+" and self._is_string_expr(expr["left"]) \
                and self._is_string_expr(expr["right"]):
            if self._in_spec:
                return f"(concat {left} {right})"
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")
            return f"(str_concat_op {left} {right})"
        # strings-plan Stage 2: string `==`/`!=` content equality. In a spec, polymorphic `=`
        # is fine (falls through below); in a program (body) context `=` on strings is not
        # usable, so bridge through `val str_eq_op : bool` (tied by `ensures` to `=`). Must
        # precede the int-coercion of `=`/`<>` below, which is only for the int-hash model.
        if raw_op in ("==", "!=") and not self._in_spec:
            ls = self._is_string_expr(expr["left"])
            rs = self._is_string_expr(expr["right"])
            if ls and rs:
                self._add_abstract_op(
                    "val str_eq_op (a: string) (b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                eq = f"(str_eq_op {left} {right})"
                return eq if raw_op == "==" else f"(not {eq})"
            if ls != rs:
                # Mixed string/int: a string compared against a genuine int (e.g. an opaque
                # decode result). Revert to legacy opaque int-equality by hashing the string
                # side, then fall through to the int `=`/`<>` path below.
                if ls:
                    left = self._str_operand_to_int(left)
                else:
                    right = self._str_operand_to_int(right)
        # In body context, coerce string literals in comparisons to int
        if not self._in_spec and op in ("=", "<>"):
            left = self._coerce_str_arg(left)
            right = self._coerce_str_arg(right)
        if op == "div":
            if self._in_spec:
                return f"(div {left} {right})"
            inner = f"(pycsl_div {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
        if op == "mod":
            if self._in_spec:
                return f"(mod {left} {right})"
            inner = f"(pycsl_mod {left} {right})"
            return self._wrap_with_no_exception_assert(("binop", raw_op), [left, right], inner)
        if op in ("&&", "||"):
            # cf6.md M1.6: `<array> or []` (`pat.get("captures", []) or []`) is the redundant
            # empty-list default — the value IS the left array (`args_of pat`). @mutable_state.
            _rr = expr.get("right", {})
            if (op == "||" and not self._in_spec
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and isinstance(_rr, dict)
                    and _rr.get("type") in ("ListLit", "ListLiteral", "ArrayLit", "List")
                    and not (_rr.get("elements") or _rr.get("elts") or _rr.get("values"))
                    and left.startswith("(args_of ")):
                return left
            # item34.md CF5: Python `<str> or <str>` (`h.get("exc_type") or "PyCSL_Exception"`)
            # returns the FIRST truthy STRING — `if not (str_eq_op a "") then a else b`. Both
            # operands string-typed, not in spec. @mutable_state.
            # resync-campaign.md R2: the right arm may be `None` (`(…).lower() or None`) → "".
            _r_none = isinstance(expr.get("right"), dict) and expr["right"].get("type") == "None"
            if (op == "||" and not self._in_spec
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())
                    and self._is_string_expr(expr["left"])
                    and (self._is_string_expr(expr["right"]) or _r_none)):
                self._add_abstract_op(
                    "val str_eq_op (a b: string) : bool\n"
                    "    ensures { result <-> (a = b) }")
                _rv = '""' if _r_none else right
                return f'(if (not (str_eq_op {left} "")) then {left} else {_rv})'
            left_b = self._to_bool(left, expr["left"])
            right_b = self._to_bool(right, expr["right"])
            if self._in_spec:
                return f"({left_b} {op} {right_b})"
            # In body context, Python's and/or return int. Use if-then-else
            # to convert bool result back to int, avoiding abstract vals
            # that can't handle mixed bool/int args.
            return f"(if {left_b} {op} {right_b} then 1 else 0)"
        if raw_op in ("in", "not in"):
            return self._emit_membership(raw_op, expr, left, right, local_refs,
                                          invariant_ctx, subst)
        # item34.md CF4: `<set> | {x}` (set union with a set literal, e.g. the for-loop's
        # `local_refs | {target}`) is a set UNION — add each element to the map — not the int
        # `bit_or`. @mutable_state; the string key is `str_hash_op`-hashed (matching M.7).
        if (raw_op == "|"
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _rset = expr.get("right", {})
            if isinstance(_rset, dict) and _rset.get("type") in ("SetLit", "Set"):
                self._add_abstract_op(
                    "val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
                    ": map 'k (option 'v)\n"
                    "    ensures { result = Map.set m k (Some v) }")
                _acc = left
                for _e in _rset.get("elts", []):
                    _ew = self._expr_to_whyml(_e, local_refs, invariant_ctx, subst)
                    _key = (f"(str_hash_op {_ew})" if self._is_string_expr(_e)
                            else self._coerce_to_int(_ew))
                    if self._is_string_expr(_e):
                        self._add_abstract_op("val str_hash_op (s: string) : int")
                    _acc = f"(map_update_some {_acc} {_key} 0)"
                return _acc
        if raw_op in self._BITWISE_FN_NAMES:
            return self._emit_bitwise_or_power(raw_op, expr, left, right)
        if raw_op == "?":
            self._add_abstract_op("val unknown_op (x: int) (y: int) : int")
            return f"(unknown_op {left} {right})"
        return f"({left} {op} {right})"

    def _iter_len_expr(self, ir: Dict[str, Any], local_refs: Set[str]) -> Optional[str]:
        """A3 (bounded eager itertools): the WhyML length of an itertools/list
        expression, or None if not recognized. `len(list(X)) == len(X)` and
        `len(chain(x0, …, xk)) == Σ len(xi)` — a chain materializes to the
        concatenation, whose length is the sum of its operands' lengths (a
        bounded, sound model: lazy/infinite iterables are out of scope). Each
        operand's length is `Array.length` (or, recursively, another chain/list)."""
        if not isinstance(ir, dict) or ir.get("type") != "Call":
            return None
        fn = ir.get("func", "")
        fn_short = fn.rsplit(".", 1)[-1] if isinstance(fn, str) else ""
        args_ir = ir.get("args", [])
        if fn_short == "list" and len(args_ir) == 1:
            inner = self._iter_len_expr(args_ir[0], local_refs)
            if inner is not None:
                return inner
            return f"(Array.length {self._expr_to_whyml(args_ir[0], local_refs)})"
        def _operand_len(sub):
            p = self._iter_len_expr(sub, local_refs)
            return p if p is not None else f"(Array.length {self._expr_to_whyml(sub, local_refs)})"
        if fn_short == "chain":
            if not args_ir:
                return "0"
            return "(" + " + ".join(_operand_len(s) for s in args_ir) + ")"
        # A3-residual: `len(product(a, b, …)) == ∏ len`; `len(islice(it, n)) ==
        # min(len(it), n)` (inline min — no MinMax import). Bounded/eager only.
        if fn_short == "product":
            if not args_ir:
                return "1"   # empty product → the single empty tuple
            return "(" + " * ".join(_operand_len(s) for s in args_ir) + ")"
        if fn_short == "islice" and len(args_ir) == 2:
            it = _operand_len(args_ir[0])
            stop = self._expr_to_whyml(args_ir[1], local_refs)
            return f"(if {it} < {stop} then {it} else {stop})"
        return None

    def _handle_len_call(self, expr: Dict[str, Any], args: List[str]) -> str:
        """Handle len(x): constant fold literals, array length in hoare model, or abstract.
        (The `len(list(chain(…)))` itertools case is resolved earlier in
        `_handle_call_expr` via `_iter_len_expr`, before the inner args are lowered.)"""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        atype = arg_ir.get("type", "")
        # §B′: len(d[k]) where d is a seq-valued dict (`Dict[_, List[int]]`) — the
        # read is a `seq int`, so its length is `Seq.length`.
        if atype == "Subscript":
            _b = arg_ir.get("value", {})
            if (isinstance(_b, dict) and _b.get("type") == "Var"
                    and getattr(self, "_dict_value_types", {}).get(_b.get("name", "")) == "seq int"):
                return f"(Seq.length {args[0]})"
        # 07-1705-rev4 P3: len() of a seq-modelled (growable) list local is `Seq.length`.
        # A seq-promoted PARAM in a CONTRACT refers to its array entry value (so fall through
        # to Array.length there — the `not _in_spec` guard); but a seq-promoted LOCAL is always
        # a seq, including in loop invariants (return-arr.md follow-on: else `len(names_out) <= i`
        # in listdir's invariant wrongly resolves to the non-existent array counter `!X_len`).
        if atype == "Var" and arg_ir.get("name") in getattr(self, "_seq_locals", set()):
            _is_param = arg_ir.get("name") in set(getattr(self, "_formal_params", []))
            if not (_is_param and self._in_spec):
                return f"(Seq.length {args[0]})"
        if atype == "String" and isinstance(arg_ir.get("value"), str):
            return str(len(arg_ir["value"]))
        if atype == "Tuple":
            return str(len(arg_ir.get("elts", [])))
        if atype in ("ArrayLit", "SetLit"):
            return str(len(arg_ir.get("elts", [])))
        if atype == "DictLit":
            return str(len(arg_ir.get("keys", [])))
        if atype == "Var":
            vname = arg_ir.get("name", "")
            known = getattr(self, "_known_collection_sizes", {})
            # Don't constant-fold against the INITIAL size if the
            # variable is an append-target — its length grows at
            # runtime, so the static fold is unsound in invariants
            # (`len(entries) <= i` collapses to `0 <= i`).
            append_targets = getattr(self, "_current_append_targets", set())
            if vname in known and vname not in append_targets:
                return str(known[vname])
            if vname in append_targets:
                # Append-target len is tracked in a sidecar ref `X_len`.
                return f"!{vname}_len"
        if self._is_string_expr(arg_ir):
            # strings-plan: len() on ANY runtime-str expression (a str var, a concat
            # `s + t`, a slice `s[a:b]`, an index `s[i]`) is the Why3 string length —
            # not just a bare str var. In a spec the logic symbol `String.length` is used
            # directly; in a program (body) context that logic symbol is not allowed, so
            # bridge it through an abstract `val` whose `ensures` ties the program result
            # to `String.length` (and `args[0]` is the already-lowered string expression).
            if self._in_spec:
                return f"(String.length {args[0]})"
            self._add_abstract_op(
                "val str_length_op (s: string) : int\n"
                "    ensures { result = (String.length s) }")
            return f"(str_length_op {args[0]})"
        if self._value_semantic:
            var_name = arg_ir.get("name", "") if atype == "Var" else ""
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_inline_array_temps", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                    is_array = True
            if is_array:
                arg0 = f"({args[0]})" if args[0].startswith("!") else args[0]
                return f"(Array.length {arg0})"
            self._add_abstract_op("val iter_length (x: int) : int")
            return f"(iter_length {args[0]})"
        return f"{args[0].lstrip('!')}_len"

    def _handle_join_call(self, expr: Dict[str, Any], args: List[str],
                          local_refs=None, invariant_ctx=False, subst=None) -> str:
        """Handle str.join(iterable): pick join_array for arrays, join_1 otherwise."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        # faithful-string-op.md §3.5: a LITERAL list/tuple of STRINGS joined by `sep`
        # lowers to nested `str_concat_op` (EXACT and faithful: `e0 ++ sep ++ e1 ++ …`),
        # not the opaque int `join_array`. `sep` is `expr['receiver']` (join reaches here
        # in the receiver form). A general/computed iterable stays on the int join below
        # (its faithful `string` model needs a `seq string` element model — deferred).
        _recv = expr.get("receiver")
        _at = arg_ir.get("type", "")
        if _recv is not None and _at in ("ArrayLit", "ListLit", "Tuple"):
            _elts = arg_ir.get("elts", [])
            if _elts and all(self._is_string_expr(e) for e in _elts):
                self._add_abstract_op(
                    "val str_concat_op (a: string) (b: string) : string\n"
                    "    ensures { result = (concat a b) }\n"
                    "    ensures { String.length result = String.length a"
                    " + String.length b }")
                _lr = local_refs or set()
                _sep = self._expr_to_whyml(_recv, _lr, invariant_ctx, subst)
                _ew = [self._expr_to_whyml(e, _lr, invariant_ctx, subst) for e in _elts]
                _acc = _ew[-1]
                for _k in range(len(_ew) - 2, -1, -1):
                    _acc = f"(str_concat_op {_ew[_k]} (str_concat_op {_sep} {_acc}))"
                return _acc
        # list-comprehension-lowering.md L2: a STRING-element array (a comprehension-bound
        # local like `tmp_names`, a `List[str]` field, a repeat/literal) joins to a `string`
        # — regardless of whether it is tracked as an `_array_locals` entry. Fires before the
        # int `is_array` path below. @mutable_state (the elem-type map is empty elsewhere).
        if self._join_arg_elem_is_string(arg_ir):
            _sep2 = (self._expr_to_whyml(_recv, local_refs or set(), invariant_ctx, subst)
                     if _recv is not None else '" "')
            # A seq-promoted (`.append`-grown) string list is a `seq string`, not `array
            # string` — use the seq-join variant (`lines = [f"…"]; lines.append(…)`).
            if (arg_ir.get("type") == "Var"
                    and arg_ir.get("name") in getattr(self, "_seq_locals", set())):
                self._add_abstract_op(
                    "val str_join_seq (sep: string) (xs: seq string) : string\n"
                    "    ensures { String.length result >= 0 }")
                return f"(str_join_seq {_sep2} {args[0]})"
            self._add_abstract_op(
                "val str_join_arr (sep: string) (xs: array string) : string\n"
                "    ensures { String.length result >= 0 }")
            return f"(str_join_arr {_sep2} {args[0]})"
        var_name = arg_ir.get("name", "") if arg_ir.get("type") == "Var" else ""
        is_array = (var_name in getattr(self, "_array_locals", set()) or
                    var_name in getattr(self, "_current_array1d_params", set()))
        if not is_array and var_name:
            if getattr(self, "_current_symbol_table", {}).get(var_name) in ("list", "dict"):
                is_array = True
        if not is_array:
            at = arg_ir.get("type", "")
            if at in ("ArrayLit", "ListLit", "ListComp"):
                is_array = True
            elif at == "BinOp" and arg_ir.get("op") == "*":
                for side in ("left", "right"):
                    if arg_ir.get(side, {}).get("type", "") in ("ArrayLit", "ListLit"):
                        is_array = True
        if not is_array and "Array.make" in args[0]:
            is_array = True
        if is_array:
            # list-comprehension-lowering.md L2: a STRING-element array joined by `sep` is a
            # `string` (general-iterable join — length ≥ 0 only; the exact literal-list join
            # is handled above). Element type from `_array_elem_types` (Var) or the literal
            # shape. @mutable_state-gated → the corpus's int `join_array` is byte-identical.
            if self._join_arg_elem_is_string(arg_ir):
                _sep = (self._expr_to_whyml(_recv, local_refs or set(), invariant_ctx, subst)
                        if _recv is not None else '" "')
                self._add_abstract_op(
                    "val str_join_arr (sep: string) (xs: array string) : string\n"
                    "    ensures { String.length result >= 0 }")
                return f"(str_join_arr {_sep} {args[0]})"
            self._add_abstract_op("val join_array (a: array int) : int")
            return f"(join_array {args[0]})"
        self._add_abstract_op("val join_1 (x: int) : int")
        return f"(join_1 {args[0]})"

    def _join_arg_elem_is_string(self, arg_ir) -> bool:
        """list-comprehension-lowering.md L2: does the join argument's array carry STRING
        elements? A Var → `_array_elem_types`; the literal comprehension/repeat/list forms →
        their element type. @mutable_state only (the map is empty elsewhere)."""
        if not isinstance(arg_ir, dict):
            return False
        t = arg_ir.get("type")
        if t == "Var":
            _n = arg_ir.get("name")
            if getattr(self, "_array_elem_types", {}).get(_n) == "string":
                return True
            if getattr(self, "_seq_value_types", {}).get(_n) == "string":
                return True
            # self-ir-schema.md IR4: a @mutable_state seq local (`seq_parts = []; .append`)
            # holds emitted CODE strings — join it as a string seq (str_join_seq). If it
            # were an int seq the WhyML would fail to type-check (loud, never silent).
            return (_n in getattr(self, "_seq_locals", set())
                    and getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set()))
        if t == "ListComp":
            return self._is_string_expr(arg_ir.get("elt", {}))
        if t in ("ArrayLit", "ListLit", "Tuple"):
            _e = (arg_ir.get("elts") or [None])[0]
            return bool(_e) and self._is_string_expr(_e)
        if t == "BinOp" and arg_ir.get("op") == "*":
            for side in ("left", "right"):
                s = arg_ir.get(side, {})
                if isinstance(s, dict) and s.get("type") in ("ArrayLit", "ListLit"):
                    _e = (s.get("elts") or [None])[0]
                    return bool(_e) and self._is_string_expr(_e)
        return False

    def _handle_sum_call(self, expr: Dict[str, Any]) -> str:
        """Handle sum(iterable): constant fold if all elements are known literals."""
        arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
        if arg_ir.get("type") == "ArrayLit":
            elts = arg_ir.get("elts", [])
            if all(e.get("type") == "Number" and isinstance(e.get("value"), (int, float))
                   for e in elts):
                return str(sum(int(e["value"]) for e in elts))
        if arg_ir.get("type") == "Var":
            vname = arg_ir.get("name", "")
            known_elems = getattr(self, "_known_collection_elements", {})
            known_sizes = getattr(self, "_known_collection_sizes", {})
            if vname in known_elems and vname in known_sizes:
                size = known_sizes[vname]
                elems = known_elems[vname]
                if all(i in elems for i in range(size)):
                    return str(sum(int(elems[i]) for i in range(size)))
        return ""

    def _resolve_dotted_signature(self, func_name: str):
        """Resolve a dotted call's `(ret_type, param_types, result_ensures, field_spec)`
        from the module method tables: `self.<m>(...)` and `<recordvar>.<m>(...)` look up
        the real declared signature + propagated result-only/param-referencing
        postconditions; a bare bytes-producing method (`encode`/`ljust`/…) returns
        `array int`. Default is `int` / no types / no ensures / no field_spec.

        `field_spec` is `None`, or `(receiver_expr, receiver_class, field_ensures)` when
        the callee has self-FIELD-referencing ensures (A2c): the call site then gives the
        abstract op a leading `(self: receiver_class)` parameter and passes
        `receiver_expr`, so `self.x` in the propagated clause binds to the receiver
        record. (Extracted from `_handle_dotted_call`.)"""
        ret_type = "int"
        param_types: List[str] = []
        result_ensures: List[Dict[str, Any]] = []
        field_spec: Optional[Any] = None
        if func_name.startswith("self."):
            # Method IR names are stored as "<class_lower>__<method>"
            # (Module5._build_function_ir), so a `self._emit_contracts` call
            # site has to be prefixed with the current class's lowercased
            # name to hit the lookup.
            method_tail = func_name[len("self."):]
            cls = self._current_self_type
            lookup_key = f"{cls}__{method_tail}" if cls else method_tail
            ret_type = self._module_method_return_types.get(lookup_key, "int")
            param_types = self._module_method_param_types.get(lookup_key, [])
            # Propagate the callee's result-only postconditions onto the
            # stub (array length, slot bounds, …) so the caller can
            # discharge VCs on the returned value. Param-referencing clauses
            # (already renamed to the stub's x_i) propagate too — e.g.
            # `\array_eq(\result, data)`.
            result_ensures = (
                getattr(self, "_module_method_result_ensures", {}).get(lookup_key, [])
                + getattr(self, "_module_method_param_result_ensures", {}).get(lookup_key, []))
            # gap7-spec-rev2 P3: fold in void/mutating contract for `self.<m>()` too.
            _fe = getattr(self, "_module_method_field_result_ensures", {}).get(lookup_key, [])
            _foe = getattr(self, "_module_method_field_old_ensures", {}).get(lookup_key, [])
            _fpe = getattr(self, "_module_method_field_param_result_ensures", {}).get(lookup_key, [])
            _fppe = getattr(self, "_module_method_field_param_post_ensures", {}).get(lookup_key, [])
            _fpfe = getattr(self, "_module_method_field_param_frame_ensures", {}).get(lookup_key, [])
            _rfe = getattr(self, "_module_method_result_frame_ensures", {}).get(lookup_key, [])
            _w = getattr(self, "_module_method_writes", {}).get(lookup_key, [])
            field_ens = _fe + _foe + _fpe + _fppe
            if (field_ens or _w or _fpfe or _rfe) and cls:
                # `self.<m>()` called from a sibling method: the enclosing
                # method's own `self` is the receiver, typed as the class. The 5th slot
                # carries the OPT-IN quantified frame ensures (M4), lowered separately with
                # the Call-trigger so only they get a trigger (non-frame ensures stay bare).
                # The 6th slot carries the OPT-IN `\result`-referencing single-cell frame
                # (fd-import-boundary), lowered with `\result` bound to the val's `result`.
                field_spec = ("self", cls, field_ens, _w, _fpfe, _rfe)
        else:
            # `<recordvar>.method(...)` — resolve the receiver's class so the
            # callee's result-only `ensures` propagates to this call site,
            # exactly like `self.method(...)`. Without this the call lowered to a
            # bare abstract op with no `ensures`, so a driver function that
            # constructs an instance and calls a method could prove nothing
            # about the result.
            matched_instance = False
            rv_classes = getattr(self, "_current_record_var_classes", {})
            # no-inline.md Piece C: also resolve a method on a MODULE-GLOBAL instance
            # (`_filesystem.sys_write(...)`) so a non-inlined call uses the callee's contract
            # (return type + result-only ensures), not the abstract int default.
            gv_classes = getattr(self, "_module_global_classes", {})
            parts = func_name.split(".")
            if len(parts) == 2 and (parts[0] in rv_classes or parts[0] in gv_classes):
                cls = (rv_classes.get(parts[0]) or gv_classes.get(parts[0])).lower()
                lookup_key = f"{cls}__{parts[1]}"
                rens = getattr(self, "_module_method_result_ensures", {})
                prens = getattr(self, "_module_method_param_result_ensures", {})
                if (lookup_key in self._module_method_return_types
                        or lookup_key in rens or lookup_key in prens):
                    ret_type = self._module_method_return_types.get(lookup_key, "int")
                    param_types = self._module_method_param_types.get(lookup_key, [])
                    result_ensures = rens.get(lookup_key, []) + prens.get(lookup_key, [])
                    fens = getattr(self, "_module_method_field_result_ensures", {})
                    # gap7-spec-rev2: also fold in the void/mutating contract — self-field
                    # `\old`-relating ensures + the `writes` (assigns) set — so a statement-position
                    # `c.inc()` mutates `c` instead of lowering to an opaque no-op.
                    foens = getattr(self, "_module_method_field_old_ensures", {})
                    fpens = getattr(self, "_module_method_field_param_result_ensures", {})
                    fppens = getattr(self, "_module_method_field_param_post_ensures", {})
                    fpfens = getattr(self, "_module_method_field_param_frame_ensures", {})
                    rfens = getattr(self, "_module_method_result_frame_ensures", {})
                    mwrites = getattr(self, "_module_method_writes", {})
                    field_ens = (fens.get(lookup_key, []) + foens.get(lookup_key, [])
                                 + fpens.get(lookup_key, []) + fppens.get(lookup_key, []))
                    writes = mwrites.get(lookup_key, [])
                    frame_ens = fpfens.get(lookup_key, [])
                    result_frame_ens = rfens.get(lookup_key, [])
                    if field_ens or writes or frame_ens or result_frame_ens:
                        # `b.<m>()`: the receiver record `b` becomes the abstract op's leading
                        # `(self: cls)` parameter; `writes` frames the mutated self-fields.
                        field_spec = (parts[0], cls, field_ens, writes, frame_ens,
                                      result_frame_ens)
                    matched_instance = True
            if not matched_instance:
                # Bytes-producing methods return `array int` (a byte buffer),
                # not the default `int` — so a chain like
                # `name.encode('utf-8')[:30].ljust(30, b'\x00')` can flow into a
                # `struct.pack('>...30s', ...)` name field. (Gap 5 of
                # missing-pycsl-ir-features.md, handled by typing the opaque op.)
                method_tail_name = func_name.rsplit(".", 1)[-1]
                if method_tail_name in ("encode", "ljust", "rjust", "zfill"):
                    ret_type = "array int"
        return ret_type, param_types, result_ensures, field_spec

    def _handle_dotted_call(self, func_name: str, args: List[str]) -> str:
        """Handle dotted method calls (x.method(...)): emit abstract val declaration."""
        # module-emission.md (§T.2.7m): a CROSS-MODULE `self.<m>(...)` call — the callee
        # lives in a DIFFERENT `#@ verify_module` group than the function currently being
        # emitted — is lowered to the callee's PROVEN interface contract via the Why3
        # `clone`-refinement interface module `<G>Sig`, NOT to an assumed abstract `val`
        # stub. The interface `val <fn>` carries the callee's real contract (proved by the
        # provider module's `'refn'vc`), so the caller gets a proven boundary with NO new
        # trust. Active only on the `_transpile_modular` path (`_verify_module_of` set);
        # default flat path leaves this dict empty → byte-identical.
        vmod_of = getattr(self, "_verify_module_of", None)
        if vmod_of and func_name.startswith("self.") and self._current_self_type:
            callee_whyml = whyml_ident(
                f"{self._current_self_type}__{func_name[len('self.'):]}")
            callee_group = vmod_of.get(callee_whyml)
            cur_group = getattr(self, "_current_emit_group", None)
            if callee_group is not None and callee_group != cur_group:
                # Resolve the callee's declared signature so the args are coerced to the
                # interface val's parameter types (the Sig `val` is emitted with the same
                # signature from the SAME maps).
                ret_type, param_types, _, _ = self._resolve_dotted_signature(func_name)
                n = len(args)
                while len(param_types) < n:
                    param_types.append("int")
                param_types = param_types[:n]
                coerced = self._coerce_dotted_args(args, param_types)
                sig_mod = f"{callee_group}Sig"
                return (f"({sig_mod}.{callee_whyml} "
                        + " ".join(["self"] + coerced) + ")").replace("  ", " ")
        # Stateful composition: when this is `self.<m>(...)` inside a composer and
        # `<self_type>__<m>` is a flattened provider (`_apply_composition`), call it
        # CONCRETELY — `(<self_type>__<m> self args)` — so the provider's full
        # state-mutating contract (`assigns self.f`, `ensures self.f == \old(...)`)
        # applies. The abstract-val lowering below drops `self` and self-field ensures
        # (the method-call contract gap), which is sound only for pure providers. A
        # mixin's own isolation method is NOT in `_composed_provider_methods`, so its
        # genuine dependency still resolves to the abstract `val`.
        if func_name.startswith("self.") and self._current_self_type:
            concrete = f"{self._current_self_type}__{func_name[len('self.'):]}"
            if concrete in getattr(self, "_composed_provider_methods", set()):
                _, c_param_types, _, _ = self._resolve_dotted_signature(func_name)
                while len(c_param_types) < len(args):
                    c_param_types.append("int")
                c_coerced = self._coerce_dotted_args(args, c_param_types[:len(args)])
                return f"({concrete} {' '.join(['self'] + c_coerced)})".rstrip()
        safe_name = whyml_ident(func_name.replace(".", "_"))
        n = len(args)
        arity_name = f"{safe_name}_{n}"
        # When the call is `self.<method>(...)` on a method defined in the
        # same module, look up the real declared return type AND parameter
        # types so the abstract val matches the actual signature. Without
        # this, every `self.foo(...)` is abstracted as `val ... (xi: int)
        # ... : int`, mismatching downstream consumers when `<method>`
        # actually takes/returns array or map types.
        ret_type, param_types, result_ensures, field_spec = self._resolve_dotted_signature(func_name)
        # Pad / truncate param_types to match n (the abstract val arity
        # only sees the caller's actual arg count, not the IR's symbol
        # table size).
        while len(param_types) < n:
            param_types.append("int")
        param_types = param_types[:n]
        # Per missing-bytes-struct-feature.md Phase 1: infer
        # array-int args from the emitted WhyML expression's shape
        # for non-self calls (where module_method_param_types
        # lookup didn't supply types). Without this, calls like
        # `struct.unpack(fmt, entry_bytes)` where `entry_bytes`
        # comes from `(array_slice self.disk ...)` were declared
        # with all-int param types, mismatching the array-int call
        # site and causing Why3 to reject the file with
        # `array.Array.array int @rho but is expected to have
        # type int`.
        ARRAY_INT_PREFIXES = (
            "(Array.make ", "(Array.sub ", "(array_slice ", "(Array.make_init ",
            "(array_copy ", "(array_concat ",
        )
        for i, arg in enumerate(args):
            if param_types[i] != "int":
                continue   # Already typed (from self-method lookup)
            stripped = arg.strip()
            if any(stripped.startswith(p) for p in ARRAY_INT_PREFIXES):
                param_types[i] = "array int"
                continue
            # Bare identifier referring to a known array-int local
            # / param. Check the symbol table.
            if stripped.startswith("!"):
                ident = stripped[1:]
            else:
                ident = stripped
            if not ident.replace("_", "").isalnum():
                continue
            st = getattr(self, "_current_symbol_table", {})
            if (ident in getattr(self, "_current_array1d_params", set())
                    or st.get(ident) in ("list", "tuple", "bytes", "bytearray")
                    or ident in getattr(self, "_array_locals", set())):
                param_types[i] = "array int"
        coerced = self._coerce_dotted_args(args, param_types)
        # A2c: a self-FIELD-referencing callee ensure (`\result == self.x`) is
        # bound by giving the abstract op a leading receiver parameter
        # `(self: <class>)` and passing the receiver record, so `self.x` in the
        # propagated clause resolves to the actual instance's field.
        receiver_param = ""
        writes_clause = ""
        if field_spec is not None:
            receiver_expr, receiver_class = field_spec[0], field_spec[1]
            receiver_param = f"(self: {receiver_class}) "
            coerced = [receiver_expr] + coerced
            # gap7-spec-rev2: a void/mutating method's `assigns self.f` → `writes { self.f }` on
            # the abstract op, so the call mutates the receiver's region (the `_dotted_ensures_suffix`
            # `\old(self.f)` clause then relates post- to pre-state, and the caller sees the change).
            writes_fields = field_spec[3] if len(field_spec) > 3 else []
            if writes_fields:
                # Why3 `writes` is COMMA-separated (a `;` is a syntax error — only shows with
                # multi-field writes like os.sys_write's disk+fd_offset+_mtime_ticks).
                writes_clause = "\n    writes { " + ", ".join(
                    f"self.{f}" for f in writes_fields) + " }"
        # allocator-frame plan §2.7 (scope-to-win): an OPT-IN `#@ sibling_concrete` callee
        # gets a CONCRETE `self.<m>()` lowering — `(<class>__<m> self args)` — so why3 uses
        # the real method's FULL contract AND its type (class) invariant guarantee on the
        # post-state (an abstract stub conveys neither). Restricted to MARKED callees so it
        # fires ONLY for cheap leaf writers whose guarantee the caller absorbs (the os bitmap
        # leaves) — NOT for heavy directory mutators (concrete-calling those surfaces their
        # expensive maintenance into the caller). Ordering (callee before caller) is supplied
        # by scc.find_self_method_calls. Default (no marker) → abstract stub, byte-identical.
        if (field_spec is not None and func_name.startswith("self.")
                and self._current_self_type):
            concrete_name = whyml_ident(
                f"{self._current_self_type}__{func_name[len('self.'):]}")
            if (concrete_name in getattr(self, "_module_func_names", set())
                    and concrete_name in getattr(self, "_sibling_concrete_methods", set())):
                return f"({concrete_name} {' '.join(coerced)})"
        # body-gate gap-1: lower the callee's `\result[i]` ensures against the
        # CALLEE's return type, not the caller's. A method returning `array int`
        # (e.g. `_read_inode`) whose ensures says `\result[0] == …` must lower
        # `\result[0]` to `result[0]` (Array.get, via the L0 path in
        # `_resolve_subscript`), NOT the opaque/unbound `subscript_get` it gets when
        # `_func_return_type` still holds the CALLER's type. Restore after.
        _saved_frt = getattr(self, "_func_return_type", "")
        self._func_return_type = ret_type
        ensures_suffix = self._dotted_ensures_suffix(result_ensures, n, param_types, field_spec)
        self._func_return_type = _saved_frt
        if n == 0 and not receiver_param:
            self._add_abstract_op(f"val {arity_name} () : {ret_type}{ensures_suffix}")
            return f"({arity_name} ())"
        params = " ".join(f"(x{i}: {ptype})" for i, ptype in enumerate(param_types))
        params = f"{receiver_param}{params}".rstrip()
        self._add_abstract_op(f"val {arity_name} {params} : {ret_type}{writes_clause}{ensures_suffix}")
        return f"({arity_name} {' '.join(coerced)})"

    def _is_seq_arg(self, arg: str) -> bool:
        """True if a lowered arg is a `seq`-typed value (a seq local or a seq-producing op), so
        `_coerce_dotted_args` can bridge it to a `List[_]` (array) param via `materialize`.
        @mutable_state-gated (seq locals only exist there) -> corpus byte-identical.
        (seq<->array-coercion feature: enables converting emitter handlers that pass list-
        comprehension results to `List[_]` helper params, e.g. `_handle_call_expr`'s `args`.)"""
        if not getattr(self, "_mutable_state_classes", None):
            return False
        base = arg.strip().lstrip("!")
        if (base in getattr(self, "_seq_locals", set())
                or base in getattr(self, "_seq_value_types", {})):
            return True
        return arg.strip().startswith(("(list_comp_seq", "(seq_sub ", "(Seq."))

    def _coerce_dotted_args(self, args: List[str], param_types: List[str]) -> List[str]:
        """Coerce each dotted-call arg to its declared param type. The caller's arg may be
        int while the param expects array or map (e.g. an int from an abstract `get_*`
        accessor flowing into a `Set[T]` slot). (Extracted from `_handle_dotted_call`.)"""
        coerced: List[str] = []
        for arg, ptype in zip(args, param_types):
            if ptype == "int":
                coerced.append(self._coerce_to_int(arg))
            elif ptype in ("array int", "array string") and self._is_seq_arg(arg):
                # seq<->array coercion: a `seq`-typed arg (a list comprehension lowers to `seq`)
                # flowing into a `List[_]` (= `array _`) param is bridged seq->array via
                # `materialize`/`materialize_str`. @mutable_state-only detection (seq locals) ->
                # byte-identical for the corpus (`_is_seq_arg` is False without _mutable_state).
                if ptype == "array string":
                    self._materialize_str_bridge()
                    coerced.append(f"(materialize_str {arg})")
                else:
                    self._materialize_bridge()
                    coerced.append(f"(materialize {arg})")
            elif ptype == "array int":
                coerced.append(self._array_coerce_arg(arg))
            elif ptype == "map int (option int)":
                # No known int→map coercion. Use `const None` as a
                # placeholder empty map; the abstract val has no axioms
                # about its contents anyway.
                stripped = arg.strip()
                map_prefixes = ("(map_update_some ", "(map_update_none ",
                                "(const (None: option int)", "(Map.get ")
                if any(stripped.startswith(p) for p in map_prefixes):
                    coerced.append(arg)
                elif stripped.replace("_", "").replace("!", "").isalnum():
                    # Bare identifier — pass through; caller-side type
                    # must already match.
                    coerced.append(arg)
                else:
                    coerced.append("(const (None: option int))")
            else:
                coerced.append(arg)
        return coerced

    @staticmethod
    def _strip_outer_parens(s: str) -> str:
        """Strip ONE matching outer paren pair if it wraps the whole string (else unchanged) —
        bares a lowered trigger term (`(slot_inode self.disk x0 k)` → `slot_inode self.disk x0 k`);
        a trigger pattern must be bare (Why3 mis-parses `[(t)]` → auto-trigger fallback)."""
        s = s.strip()
        if not (s.startswith("(") and s.endswith(")")):
            return s
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return s[1:-1].strip() if i == len(s) - 1 else s
        return s

    def _frame_trigger_term(self, node: Any) -> Optional[Dict[str, Any]]:
        """For a frame conjunct `X == \\old(...)` (or `\\old(...) == X`) anywhere in `node`,
        return X's IR — the POST-state term to pin as the forall's E-matching trigger (first
        match, depth-first), else None."""
        if not isinstance(node, dict):
            return None
        if node.get("type") == "BinOp" and node.get("op") == "==":
            l, r = node.get("left"), node.get("right")
            l_old = isinstance(l, dict) and l.get("type") in ("Old", "OldField")
            r_old = isinstance(r, dict) and r.get("type") in ("Old", "OldField")
            if r_old and not l_old:
                return l
            if l_old and not r_old:
                return r
        for v in node.values():
            for c in (v if isinstance(v, list) else [v]):
                res = self._frame_trigger_term(c)
                if res is not None:
                    return res
        return None

    def _dotted_ensures_suffix(self, result_ensures: List[Dict[str, Any]], n: int,
                               param_types: List[str],
                               field_spec: Optional[Any] = None) -> str:
        """Render the propagated postconditions of a dotted callee as
        `\\n    ensures { … }` lines appended to its abstract `val`. Emitted in spec
        (boolean) context with the stub's positional params x0..x{n-1} registered as
        in-scope.

        `field_spec` (A2c) carries `(receiver_expr, receiver_class, field_ensures)` of
        self-FIELD clauses: these are rendered with `_current_self_type` set to the
        receiver class so the leading `(self: <class>)` op parameter binds `self.x` (and
        ambiguous field labels qualify correctly). (Extracted from `_handle_dotted_call`.)"""
        field_ensures = field_spec[2] if field_spec is not None else []
        frame_ensures = (field_spec[4] if field_spec is not None and len(field_spec) > 4
                         else [])
        result_frame_ensures = (field_spec[5] if field_spec is not None and len(field_spec) > 5
                                else [])
        if (not result_ensures and not field_ensures and not frame_ensures
                and not result_frame_ensures):
            return ""
        _prev_spec = self._in_spec
        _prev_params = self._current_params
        self._in_spec = True   # emit boolean formulas, not int-coerced
        # The stub's positional params are x0..x{n-1}; a propagated
        # param-referencing ensures (e.g. `\array_eq(result, x0)`) names
        # them, so register them as in-scope params — otherwise
        # `_handle_var_expr` would mistake `x_i` for an undeclared global
        # and emit a spurious `val constant x_i : int`.
        self._current_params = set(_prev_params) | {
            f"x{i}" for i in range(max(n, len(param_types)))}
        ensures_suffix = ""
        for e in result_ensures:
            w = self._expr_to_whyml(e, set(), invariant_ctx=True)
            ensures_suffix += f"\n    ensures {{ {w} }}"
        if field_ensures or frame_ensures or result_frame_ensures:
            _prev_self = self._current_self_type
            self._current_self_type = field_spec[1]   # receiver class
            for e in field_ensures:
                w = self._expr_to_whyml(e, set())
                ensures_suffix += f"\n    ensures {{ {w} }}"
            # M4: the OPT-IN quantified frame ensures — lowered with `_frame_trigger_active`
            # so the Forall handler pins a specific Call-trigger (`[slot_inode self.disk x0 k]`);
            # only these clauses get a trigger, so the others stay byte-identical.
            if frame_ensures or result_frame_ensures:
                _prev_ft = self._frame_trigger_active
                self._frame_trigger_active = True
                for e in frame_ensures:
                    w = self._expr_to_whyml(e, set())
                    ensures_suffix += f"\n    ensures {{ {w} }}"
                # fd-import-boundary: the `\result`-referencing single-cell frame. `\result`
                # lowers to the val's `result` keyword (its return value = the call result),
                # so binding is automatic. A self-field Subscript post-state term carries no
                # Call-trigger (the Forall handler only pins Call triggers), so Why3 auto-
                # triggers the single-cell frame — sound for the per-cell fd_open frame.
                for e in result_frame_ensures:
                    w = self._expr_to_whyml(e, set())
                    ensures_suffix += f"\n    ensures {{ {w} }}"
                self._frame_trigger_active = _prev_ft
            self._current_self_type = _prev_self
        self._current_params = _prev_params
        self._in_spec = _prev_spec
        return ensures_suffix

    def _handle_struct_call(
            self, expr: Dict[str, Any], args: List[str],
            func_name: str) -> Optional[str]:
        """Format-string-aware emission for `struct.pack` / `struct.unpack`.

        Per missing-bytes-struct-feature.md Phase 2. Returns the
        emitted WhyML expression, or None if the format string is
        dynamic / contains unsupported chars (caller falls back to
        the generic auto-trust path).
        """
        ir_args = expr.get("args", [])
        if not ir_args:
            return None
        fmt_ir = ir_args[0]
        if fmt_ir.get("type") != "String":
            return None   # Dynamic format string
        fmt = fmt_ir.get("value", "")
        parsed = parse_format(fmt)
        if parsed is None:
            return None   # Unsupported char in format

        slot_id = parsed.slot_id()
        # cleared-pack: a single standard-size unsigned-int slot lowers to the
        # FAITHFUL, guarded `Pycsl.Struct.Std` family (`struct_{pack,unpack}_f<sig>`)
        # — byte-codec-anchored round-trip + size law + in-range guard. All other
        # shapes keep the opaque abstract `iN` symbols (documented boundary).
        faithful = parsed.faithful_uint_slot()
        if func_name == "struct.unpack":
            # struct.unpack(fmt, data) → (t1, ..., tN)
            # Abstract: val struct_unpack_<slot_id> (fmt: int) (data: array int) : (t1, ..., tN)
            if parsed.arity == 0:
                ret_type = "unit"
            elif parsed.arity == 1:
                ret_type = parsed.slots[0]
            else:
                ret_type = "(" + ", ".join(parsed.slots) + ")"
            if faithful is not None:
                sig, _w, _hi = faithful
                sym = f"struct_unpack_f{sig}"
            else:
                sym = f"struct_unpack_{slot_id}"
            # `val function` — both program-callable and a logical
            # symbol the round-trip axiom can name.
            self._add_abstract_op(
                f"val function {sym} (fmt: int) (data: array int) : {ret_type}")
            # The fmt arg is a String literal → coerce to int hash;
            # the data arg should already be `array int`-shaped.
            fmt_arg = self._coerce_str_arg(args[0]) if args else "0"
            data_arg = args[1] if len(args) > 1 else "(Array.make 0 0)"
            return f"({sym} {fmt_arg} {data_arg})"

        if func_name == "struct.pack":
            # struct.pack(fmt, x1, ..., xN) → array int
            # Abstract: val struct_pack_<slot_id> (fmt: int) (x1: t1) ... (xN: tN) : array int
            # `*list` spread: PyCSL's IR may not expose individual
            # elements when the arg is Starred. If the actual arg
            # count after fmt doesn't match the format arity, we
            # bail out and let the dotted-call path auto-trust.
            value_args = args[1:]
            if len(value_args) != parsed.arity:
                return None
            if faithful is not None:
                sig, _w, _hi = faithful
                sym = f"struct_pack_f{sig}"
            else:
                sym = f"struct_pack_{slot_id}"
            params = ["(fmt: int)"] + [
                f"(x{i}: {t})" for i, t in enumerate(parsed.slots)]
            self._add_abstract_op(
                f"val function {sym} {' '.join(params)} : array int")
            fmt_arg = self._coerce_str_arg(args[0]) if args else "0"
            # Coerce each value arg based on its slot type.
            coerced = []
            for arg, slot_t in zip(value_args, parsed.slots):
                if slot_t == "int":
                    coerced.append(self._coerce_to_int(arg))
                else:
                    coerced.append(arg)   # array int passed through
            return f"({sym} {fmt_arg} {' '.join(coerced)})"

        return None

    def _emit_contract_logic_symbol(self, func_name: str, expr: Dict[str, Any],
                                    args: List[str]) -> Optional[str]:
        """11-0632-spec-8 Part 2 (NARROW safety net, contract position only).

        An unknown applied symbol seen in CONTRACT/formula context (`_in_spec`) is a
        LOGIC predicate reference — emit it as a logic `predicate name argtypes`, NOT a
        program `val name_N (x0:int):int` (the latter is illegal in `ensures`/`requires`
        and mistyped against a `string`/`real` argument). Argument types are recovered
        from the enclosing stub's symbol table (`_current_symbol_table`) at the SAME
        py→WhyML mapping the rest of the emitter uses (`_symtype_to_whyml`: `str`→string,
        `float`→real, list/tuple/bytes→array int, default int). Returns the logic
        application `(name args)`, or None if the symbol is unsuitable for the logic path
        (then the caller keeps the program-`val` fallback).

        Faithfulness: the predicate carries NO axioms — it is an uninterpreted logic
        symbol that constrains nothing it should not. Part 1 (carrying the dependency's
        real `#@ inductive` decl) always WINS when it can: a propagated decl puts
        `func_name` in `_inductive_preds`, so this arm is never reached for it.
        """
        raw_args = expr.get("args", [])
        if len(raw_args) != len(args):
            return None
        # gap-9: if `func_name` is an imported `#@ inductive` predicate whose
        # RULE we deliberately did NOT cross (it carries a heavy `\exists`
        # trigger), recover its param types from the recorded dependency
        # signature so the opaque `predicate` decl has the RIGHT types (e.g.
        # `(array int) (string)` for `name_present(disk, name)`), not the
        # symbol-table-recovered `int` default (which mistypes `self.disk`).
        imported_sigs = getattr(self, "_imported_inductive_sigs", {}) or {}
        if func_name in imported_sigs:
            from module6_whyml.identifiers import whyml_ident as _wi
            sig_types = self._inductive_sig_whyml(imported_sigs[func_name])
            name = _wi(func_name)
            if sig_types:
                self._add_abstract_op(f"predicate {name} {sig_types}")
            else:
                self._add_abstract_op(f"predicate {name}")
            return f"({name} {' '.join(args)})" if args else name
        symtab = getattr(self, "_current_symbol_table", {}) or {}
        argtypes: List[str] = []
        for a_ir in raw_args:
            sym_t = None
            if isinstance(a_ir, dict) and a_ir.get("type") == "Var":
                sym_t = symtab.get(a_ir.get("name"))
            argtypes.append(self._symtype_to_whyml(sym_t))
        name = whyml_ident(func_name)
        if argtypes:
            self._add_abstract_op(
                f"predicate {name} {' '.join(f'({t})' for t in argtypes)}")
        else:
            self._add_abstract_op(f"predicate {name}")
        return f"({name} {' '.join(args)})" if args else name

    @staticmethod
    def _is_null_byte_lit(ir: Dict[str, Any]) -> bool:
        """True iff `ir` is the byte literal `b'\\x00'` — represented in the IR as an
        `ArrayLit` of a single `Number 0` (the bytes literal lowering)."""
        if ir.get("type") != "ArrayLit":
            return False
        elts = ir.get("elts", [])
        return (len(elts) == 1
                and elts[0].get("type") == "Number"
                and elts[0].get("value") == 0)

    def _linear_form(self, ir: Dict[str, Any]) -> Optional[Tuple[int, Dict[str, int]]]:
        """Evaluate an integer IR node to an AFFINE form (const, {var: coeff}) over
        `BinOp(+/-/*)` of `Number` and `Var` leaves. Returns None if any sub-term is
        non-affine (e.g. var*var, a Call, a Subscript). Used to compute the NULL-padded
        field WIDTH `upper - lower` as a literal even though both bounds carry the loop
        variable `i`: the difference cancels `i` and folds to the constant `30`, the
        SAME literal width the cross-validated `slot_name_byte_decode` /
        `field_to_str_round_trip` axioms key on."""
        t = ir.get("type")
        if t == "Number":
            v = ir.get("value")
            if isinstance(v, (int, float)) and float(v).is_integer():
                return (int(v), {})
            return None
        if t == "Var":
            return (0, {ir.get("name", ""): 1})
        if t == "BinOp":
            lf = self._linear_form(ir.get("left", {}))
            rf = self._linear_form(ir.get("right", {}))
            if lf is None or rf is None:
                return None
            (lc, lv), (rc, rv) = lf, rf
            op = ir.get("op")
            if op in ("+", "-"):
                sgn = 1 if op == "+" else -1
                out = dict(lv)
                for k, c in rv.items():
                    out[k] = out.get(k, 0) + sgn * c
                return (lc + sgn * rc, {k: c for k, c in out.items() if c != 0})
            if op == "*":
                # affine only if one side is a pure constant
                if not lv:
                    return (lc * rc, {k: lc * c for k, c in rv.items()})
                if not rv:
                    return (lc * rc, {k: rc * c for k, c in lv.items()})
            return None
        return None

    def _static_width(self, lower_ir: Dict[str, Any],
                      upper_ir: Dict[str, Any]) -> Optional[int]:
        """The field WIDTH `upper - lower` as a literal int, or None if it is not a
        constant (var-coefficients must all cancel)."""
        lf = self._linear_form(lower_ir)
        uf = self._linear_form(upper_ir)
        if lf is None or uf is None:
            return None
        (lc, lv), (uc, uv) = lf, uf
        diff_vars = dict(uv)
        for k, c in lv.items():
            diff_vars[k] = diff_vars.get(k, 0) - c
        if any(c != 0 for c in diff_vars.values()):
            return None
        return uc - lc

    def _match_field_decode_idiom(
            self, expr: Dict[str, Any]
    ) -> Optional[tuple]:
        """PURE STRUCTURAL match of the null-terminated-field NAME-decode idiom

            <arr>[<a>:<b>].split(b'\\x00')[0].decode('utf-8', errors='ignore')

        Returns `(slice_node, lower_ir, width)` when ALL five narrowness
        conditions (see `_recognize_field_decode_idiom`) hold, else None.

        Factored out so BOTH the value-lowering recognizer AND the
        local-VARIABLE typing pass key on the SAME shape: the recognizer
        lowers the matched value to a `field_to_str …` STRING term, so any
        local assigned this idiom must be declared a string-typed ref (never
        `ref 0 : ref int`). It performs NO emission (no `_expr_to_whyml`), so
        it is safe to call during the pre-declaration classification pass."""
        # (1) outer decode('utf-8', ...)
        if not isinstance(expr, dict):
            return None
        dargs = expr.get("args", [])
        if not dargs or dargs[0].get("type") != "String" \
                or dargs[0].get("value") != "utf-8":
            return None
        recv = expr.get("receiver")
        if not isinstance(recv, dict):
            return None
        # (2) receiver is Subscript[0]
        if recv.get("type") != "Subscript":
            return None
        idx = recv.get("index", {})
        if idx.get("type") != "Number" or idx.get("value") != 0:
            return None
        split_call = recv.get("value", {})
        # (3) ... over a `split(b'\x00')` Call
        if split_call.get("type") != "Call":
            return None
        sfunc = split_call.get("func", "")
        if not (sfunc == "split" or (isinstance(sfunc, str) and sfunc.endswith(".split"))):
            return None
        sargs = split_call.get("args", [])
        if len(sargs) != 1 or not self._is_null_byte_lit(sargs[0]):
            return None
        slice_node = split_call.get("receiver", {})
        # (4) ... whose receiver is a genuine `arr[a:b]` slice
        if slice_node.get("type") != "SliceAccess":
            return None
        sl = slice_node.get("slice", {})
        if sl.get("type") != "Slice" or sl.get("step") is not None:
            return None
        lower_ir = sl.get("lower")
        upper_ir = sl.get("upper")
        if lower_ir is None or upper_ir is None:
            return None
        # (5) statically-known field WIDTH (upper - lower), even though both bounds
        # carry the loop variable: the affine difference cancels it to the constant.
        width = self._static_width(lower_ir, upper_ir)
        if width is None or width <= 0:
            return None
        return (slice_node, lower_ir, width)

    def _recognize_field_decode_idiom(
            self, expr: Dict[str, Any], local_refs: Set[str],
            invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> Optional[str]:
        """FAITHFUL READ-NAME LOWERING (the narrow null-terminated-field recognizer).

        Match EXACTLY the on-disk fixed-width null-padded NAME-field decode idiom

            <arr>[<a>:<b>].split(b'\\x00')[0].decode('utf-8', errors='ignore')

        over a byte-array SLICE, and lower it to the genuine codec TERM

            (field_to_str <arr> <a> <b-a>)

        — the SAME abstract `field_to_str` symbol the cross-validated
        `field_to_str_round_trip` / `field_to_str_frame` / `slot_name_byte_decode`
        axioms constrain (declared `val function`, so it is program-callable). This is a
        faithful Python->WhyML lowering, NOT a `val`/assumed-ensures shim and NOT a new
        trust: `bytes[a:b].split(b'\\x00')[0].decode('utf-8', errors='ignore')` IS the
        bytes from `a` up to the first null within the `b-a`-byte window, read as a
        UTF-8 string — exactly `field_to_str`'s scan-to-first-null definition.

        NARROWNESS (provably corpus-confined): EVERY one of the following must hold, or
        the recognizer declines (returns None, leaving every other `.split`/`.decode`
        use on its existing path, byte-identical):
          1. the outer call is `decode` with first arg the string literal `'utf-8'`;
          2. its receiver is `Subscript[0]` (the `[0]` first split-part);
          3. over a `split` Call whose sole arg is the byte literal `b'\\x00'`;
          4. whose receiver is a `SliceAccess` (`arr[a:b]`, a genuine `[a:b]` slice);
          5. with a statically-known field WIDTH `b-a` (so the term carries the literal
             width the round-trip axiom keys on).
        Any other `split`/`decode` shape (non-`b'\\x00'` separator, non-`[0]` index,
        non-utf8 codec, non-slice receiver, dynamic width) is NOT matched."""
        m = self._match_field_decode_idiom(expr)
        if m is None:
            return None
        slice_node, lower_ir, width = m
        base = slice_node.get("value", {})
        arr = self._array_coerce_arg(
            self._expr_to_whyml(base, local_refs, invariant_ctx, subst))
        off = self._expr_to_whyml(lower_ir, local_refs, invariant_ctx, subst)
        # Genuine codec TERM — the abstract `field_to_str` symbol the axioms key on
        # (declared `val function` in preamble._AXIOM_FUNCTIONS, no ensures/shim).
        return f"(field_to_str {arr} {off} {width})"

    def _handle_call_expr(self, node: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        func_name = expr["func"]
        # typed-ir-for-b-ceiling.md B-C2: an INLINE `<node>.to_dict()` (no args) in a
        # @mutable_state method is IDENTITY on the typed IR — the node already IS its
        # `emit_ir` value — so lower to the receiver (the BOUND form is R1's alias).
        if (isinstance(func_name, str) and func_name.endswith(".to_dict")
                and not expr.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _recv = func_name[:-len(".to_dict")]
            _parts = _recv.split(".")
            _rir = {"type": "Var", "name": _parts[0]}
            for _p in _parts[1:]:
                _rir = {"type": "Attribute", "object": _rir, "attr": _p}
            _rw = self._expr_to_whyml(_rir, local_refs, invariant_ctx, subst)
            # An emit_ir receiver (an ExprIR field / alias) → IDENTITY (it already IS its
            # emit_ir value). item34.md CF2: a record-typed receiver (`stmt.to_dict()` on an
            # `IfStmt`/`WhileStmt` record) is a CONVERSION to the reflectable emit_ir node —
            # an opaque abstract (content unmodeled; only the emit_ir TYPE matters).
            if self._is_emit_ir_expr(_rir):
                return _rw
            self._add_abstract_op("val to_emit_ir (x: 'a) : emit_ir")
            return f"(to_emit_ir {_rw})"
        # item34.md CF4: `<set/dict>.copy()` (`declared_refs.copy()`) is IDENTITY in the
        # immutable-map model (a Why3 `map` is a value) — return the receiver map. @mutable_state.
        if (isinstance(func_name, str) and func_name.endswith(".copy")
                and not expr.get("args")
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _cr = func_name[:-len(".copy")]
            _cp = _cr.split(".")
            _cir = {"type": "Var", "name": _cp[0]}
            for _p in _cp[1:]:
                _cir = {"type": "Attribute", "object": _cir, "attr": _p}
            return self._expr_to_whyml(_cir, local_refs, invariant_ctx, subst)
        # list-comprehension-lowering.md L7: `re.findall(pat, s)` → an abstract `array
        # string` (a list of matched substrings) with STRING args — modeled BEFORE the
        # generic arg-coercion (which would hash the pattern literal to int). Content
        # unmodeled (sound); only the type + `len` matter. @mutable_state-gated.
        if (isinstance(func_name, str) and func_name.endswith(".findall")
                and len(expr.get("args", [])) == 2
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _a = expr["args"]
            _p = self._expr_to_whyml(_a[0], local_refs or set(), invariant_ctx, subst)
            _s = self._expr_to_whyml(_a[1], local_refs or set(), invariant_ctx, subst)
            self._add_abstract_op("val findall_str (pat s: string) : array string")
            return f"(findall_str {_p} {_s})"
        # item34.md CF5: `<string>.split(sep)` (whole-list form, `exc.split("|")`) → a name
        # list, seq-ified at the source (`snapshot`) → `seq string`. @mutable_state + string
        # receiver. Distinct from the `<split>[i]` element form (`str_split_elem_op`).
        if (isinstance(func_name, str) and func_name.endswith(".split")
                and len(expr.get("args", [])) == 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())
                and self._is_string_expr({"type": "Var", "name": func_name[:-len(".split")]})):
            _sep = self._expr_to_whyml(expr["args"][0], local_refs or set(), invariant_ctx, subst)
            _recvw = self._expr_to_whyml(
                {"type": "Var", "name": func_name[:-len(".split")]}, local_refs or set(),
                invariant_ctx, subst)
            self._add_abstract_op("val str_split_op (s sep: string) : array string")
            self._seq_snapshot_op()
            return f"(snapshot (str_split_op {_recvw} {_sep}))"
        # no-more-int: `x.__str__()` / `super().__str__()` returns a `string` (the Python
        # str dunder), not the opaque int the generic dotted-call assigns — so a `-> str`
        # method returning `super().__str__()` (errors.py `message`) type-checks. Faithful and
        # universal; byte-clean (no corpus driver calls `.__str__()`).
        if (isinstance(func_name, str)
                and (func_name == "__str__" or func_name.endswith(".__str__"))
                and not expr.get("args")):
            self._add_abstract_op("val str_dunder_op () : string")
            return "(str_dunder_op ())"
        # item34.md CF2: `IRScanner.<pred>(<stmt-list>)` (e.g. `ends_with_return`,
        # `has_early_return`) is a bool predicate over a `array int` stmt list — its abstract
        # takes `array int` (matching the `list_comp_stmts` arg), not the default int.
        # @mutable_state-gated (the corpus's IRScanner calls, if any, keep the int param).
        if (isinstance(func_name, str) and func_name.startswith("IRScanner.")
                and len(expr.get("args", [])) == 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _tail = func_name[len("IRScanner."):]
            _mname = whyml_ident("IRScanner_" + _tail)
            _aw = self._expr_to_whyml(expr["args"][0], local_refs or set(), invariant_ctx, subst)
            # item34.md CF5 (uniform seq): `find_*`/`collect_*` return a NAME-collection —
            # modelled as an immutable, reassignable `seq string` (a `ref (array _)` can't be
            # rebound). The abstract yields a fresh `array string`; `snapshot` at the SOURCE
            # makes it `seq string` so every downstream use is uniformly seq (no array/seq
            # mix). The `has_*`/`ends_with_*`/`uses_*` predicates stay int (bool).
            if _tail.startswith("find_") or _tail.startswith("collect_"):
                self._add_abstract_op(f"val {_mname} (l: array int) : array string")
                self._seq_snapshot_op()
                return f"(snapshot ({_mname} {_aw}))"
            self._add_abstract_op(f"val {_mname} (l: array int) : int")
            return f"({_mname} {_aw})"
        # self-ir-schema.md IR1: `self.ir.get("shared_vars", [])` → the typed slice
        # `(ir_shared_vars self.ir)` : `array sharedvar` (an opaque array of shared-var
        # records with string `name`/`mutex` fields). Content unmodeled; only the element
        # TYPE matters (so the comprehension over it is `array string`). @mutable_state.
        if (isinstance(func_name, str) and func_name == "self.ir.get"
                and len(expr.get("args", [])) >= 1
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _k0 = expr["args"][0]
            if (isinstance(_k0, dict) and _k0.get("type") == "String"
                    and _k0.get("value") == "shared_vars"):
                self._add_abstract_op("val ir_shared_vars (ir: int) : array sharedvar")
                return "(ir_shared_vars 0)"
        # A3 (bounded itertools): resolve `len(list(chain(…)))` / `len(chain(…))`
        # to a sum of `Array.length` BEFORE lowering the inner args, so the
        # opaque `chain_*`/`list_new` abstract ops are never emitted.
        if func_name == "len" and len(expr.get("args", [])) == 1:
            # B-C5: `len(<emit_ir>.get("args"))` → `nargs_of` (Call arity).
            _ar = self._emit_ir_args_recv_ir(expr["args"][0])
            if _ar is not None:
                return (f"(nargs_of {self._expr_to_whyml(_ar, local_refs or set(), invariant_ctx, subst)})")
            _le = self._iter_len_expr(expr["args"][0], local_refs or set())
            if _le is not None:
                return _le
        args = [self._expr_to_whyml(a, local_refs, invariant_ctx, subst) for a in expr["args"]]

        # faithful-string-op.md §3.1–3.3: `.replace`/`.lower`/`.upper`/`.strip` on a
        # string receiver → a faithful `string`-typed op, BEFORE the generic dotted-call
        # fallback (which would emit an opaque int). Gated on a string receiver, so
        # `datetime.replace`/`dataclasses.replace` (non-string) stay on the opaque path.
        _svm = self._handle_string_value_method(expr, args, local_refs, invariant_ctx, subst)
        if _svm is not None:
            return _svm

        # FAITHFUL READ-NAME LOWERING (null-terminated byte-field decode recognizer).
        # Recognize the EXACT idiom `arr[a:b].split(b'\x00')[0].decode('utf-8', ...)`
        # over a byte-array slice and lower it to the genuine codec TERM
        # `field_to_str arr a (b-a)` — a faithful Python->WhyML lowering (same trust
        # class as lowering `+` to integer add), NOT a per-program trust / val-shim.
        # Must run BEFORE the generic `decode` -> opaque-int / decode_str_n paths.
        if func_name == "decode":
            fd = self._recognize_field_decode_idiom(expr, local_refs,
                                                    invariant_ctx, subst)
            if fd is not None:
                return fd

        # sum-types: an applied `#@ datatype` constructor (`Circle(5)`) builds the variant.
        if func_name in self._constructors:
            return f"({func_name} {' '.join(args)})" if args else func_name

        # inductive.md: an applied inductive predicate (`even(0)`, `wf(JArr(h, s))`)
        # is a logic-level predicate application — emit `(p args)` directly (raw args,
        # no int-coercion, no abstract op), exactly like a constructor application.
        if func_name in getattr(self, "_inductive_preds", set()):
            p = whyml_ident(func_name.lower())
            return f"({p} {' '.join(args)})" if args else p

        # Axiom-backing logic functions (`_AXIOM_FUNCTIONS`, e.g.
        # `dir_lookup`/`slot_inode`/`slot_name` for UnixFs.Dir): a contract call
        # is a raw logic application bound to the registry symbol — NO int
        # coercion (args keep their faithful array/int/string types) and NO
        # arity-suffixed abstract op. This is the risk-2 binding: it ties
        # `_dir_lookup`'s ensures and the `name_present` rule to the SAME symbols
        # the axiom constrains, so the citation constrains the REAL scan.
        if func_name in getattr(self, "_axiom_logic_funcs", set()):
            return f"({func_name} {' '.join(args)})" if args else func_name

        # missing-bytes-struct-feature.md Phase 2 — struct.pack /
        # struct.unpack get a format-string-aware abstract emission
        # before falling through to the generic dotted-call path.
        if func_name in ("struct.pack", "struct.unpack"):
            handled = self._handle_struct_call(expr, args, func_name)
            if handled is not None:
                return handled
            # fmt is dynamic / unsupported chars → fall through to
            # generic _handle_dotted_call (which auto-trusts).

        named = self._call_named_builtins(expr, args, func_name, local_refs,
                                          invariant_ctx, subst)
        if named is not None:
            return named
        if "." in func_name:
            return self._handle_dotted_call(func_name, args)
        rec = self._call_record_constructor(args, func_name)
        if rec is not None:
            return rec
        bytes_call = self._call_bytes_methods(args, func_name)
        if bytes_call is not None:
            return bytes_call
        # str-list-elements: `bytes.decode(...)` produces a `str`. When the surrounding
        # assignment binds the result to a STRING-typed local (`self._decode_to_string`),
        # lower it to a string-returning val so the decoded `name` is a `string` (feeding
        # `seq string` / a string-typed consumer like sys_stat). Otherwise decode stays in
        # the legacy opaque INT model (byte-identical for every non-string-list caller).
        if func_name == "decode" and getattr(self, "_decode_to_string", False):
            n = len(args)
            arity_fn = f"decode_str_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : string")
                return f"({arity_fn} ())"
            params = " ".join(f"(x{i}: int)" for i in range(n))
            self._add_abstract_op(f"val {arity_fn} {params} : string")
            coerced = [self._coerce_to_int(a) for a in args]
            return f"({arity_fn} {' '.join(coerced)})"
        safe_fn = whyml_ident(func_name)
        if (func_name not in local_refs
                and func_name not in self._current_params
                and safe_fn not in self._module_func_names):
            # 11-0632-spec-8 Part 2 (safety net, NARROW): in CONTRACT/formula
            # position (`_in_spec`), an unknown applied symbol is a LOGIC predicate
            # reference (a `present(filepath)`-shaped contract symbol whose decl did
            # NOT cross the import boundary — e.g. the dependency forgot to declare it,
            # or a shape Part 1 does not yet carry). A program `val …:int` is illegal
            # in `ensures`/`requires`, so emit a logic `predicate`/`function` instead,
            # with arg types recovered from the enclosing stub's symbol table (NOT the
            # int model). Part 1 always wins when it can supply the real decl (then
            # `func_name` is in `_inductive_preds` and this arm is never reached). This
            # fires ONLY in `_in_spec` AND while emitting a bodyless `val`/trusted-stub
            # contract (`_emitting_val_contract`) — body-position unannotated calls keep
            # the program `val` below, and a real `let` function whose `ensures`
            # references a symbol it ALSO program-calls (0386) keeps its program `val`.
            if (getattr(self, "_in_spec", False)
                    and getattr(self, "_emitting_val_contract", False)):
                logic = self._emit_contract_logic_symbol(func_name, expr, args)
                if logic is not None:
                    return logic
            # Unannotated callee: no signature is known, so the abstract op and
            # its args stay in the int model.
            coerced_args = [self._coerce_to_int(a) for a in args]
            n = len(coerced_args)
            arity_fn = f"{safe_fn}_{n}"
            if n == 0:
                self._add_abstract_op(f"val {arity_fn} () : int")
            else:
                self._add_abstract_op(
                    f"val {arity_fn} {' '.join(f'(x{i}: int)' for i in range(n))} : int")
            # Strict-propagation mode (workplan §1.4): an unannotated
            # callee called from a function with `no_exception` is
            # treated pessimistically. Default mode preserves backward
            # compat — ambient.
            inner = f"({arity_fn} {' '.join(coerced_args) if coerced_args else '()'})"
            return self._wrap_unannotated_call_with_strict_assert(inner)
        # 1111-spec R7 (no-more-int): if the call passes fewer args than the callee
        # arity, fill the missing trailing params from the callee's positional
        # defaults (lowered at the param's real type via R5 below) so the application
        # is total — never a partial application. A missing param with no default is a
        # hard error, not a silent partial application.
        formal_params = self._module_method_formal_params.get(func_name, [])
        if formal_params and len(args) < len(formal_params):
            defaults = self._module_method_param_defaults.get(func_name, {})
            for nm in formal_params[len(args):]:
                if nm in defaults:
                    # 10-1732-gap (Gap 3, no-more-int): a `None` default on a non-int
                    # param lowers to the int-model sentinel `0`, which is ill-typed
                    # against a `string`/`real` param. Fill the param's FAITHFUL zero
                    # instead, keyed on the by-name WhyML param-type map (covers
                    # imported `\trusted` stubs, built from the same funcs_for_maps).
                    # Scope: str/real (R3); any other non-int type falls back to `0`
                    # (status quo, no worse than today — record/array/map deferred).
                    dflt_ir = defaults[nm]
                    pwt = getattr(self, "_module_method_param_whyml_types", {}).get(
                        func_name, {}).get(nm, "int")
                    if dflt_ir.get("type") == "None" and pwt != "int":
                        filled = {"string": '""', "real": "0.0"}.get(pwt, "0")
                    else:
                        filled = self._expr_to_whyml(dflt_ir, local_refs,
                                                     invariant_ctx, subst)
                    args = args + [filled]
                else:
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        f"call to '{func_name}' passes {len(expr.get('args', []))} "
                        f"positional argument(s) but parameter '{nm}' has no default "
                        f"(arity {len(formal_params)}).")
        # Known module function (incl. an imported trusted stub). Coerce each arg to
        # the callee's REAL declared parameter type (1111-spec R5, no-more-int): a
        # `string` arg to a `string` param flows as a Why3 string, NOT an int hash; a
        # `list` arg to an `array int` param stays an array; etc. Without the
        # signature, fall back to the int model.
        param_types = self._module_method_param_types.get(func_name, [])
        if param_types:
            coerced_args = self._coerce_dotted_args(args, param_types[:len(args)])
        else:
            coerced_args = [self._coerce_to_int(a) for a in args]
        # User-function call site. Look up the callee's raises summary;
        # if any clause names an exception the caller has committed to
        # avoid, prepend an assertion that the raises condition cannot
        # hold under the actual args.
        inner = f"({safe_fn} {' '.join(coerced_args) if coerced_args else '()'})"
        return self._wrap_call_with_callee_raises_assert(func_name, inner, args)

    def _content_string_method(self, expr: Dict[str, Any], args: List[str],
                               func_name: str, local_refs: Set[str],
                               invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> Optional[str]:
        """strings-plan Stage 3: content-aware `str` methods with a substring-based witness.

        `s.startswith(p)` / `s.endswith(p)` / `s.find(sub)` are lowered to abstract ops whose
        `ensures` relate the (int) result to `String.substring` over the *receiver as an
        operand*. Applies ONLY to a simple, `str`-typed receiver with a single string
        argument; a chained receiver (`node.name.startswith(…)`) or a non-`str` receiver
        falls through to the opaque baked-into-the-name predicate path. startswith/endswith
        keep the 0/1 int result (so control-flow / `\result ∈ {0,1}` uses are unaffected) and
        gain a `(result = 1) <-> <substring condition>` clause; find returns an index ≥ -1
        with a found-index witness."""
        if "." not in func_name:
            return None
        recv, method = func_name.rsplit(".", 1)
        if method not in ("startswith", "endswith", "find"):
            return None
        if "." in recv or self._current_symbol_table.get(recv) != "str":
            return None
        if len(args) != 1 or not self._is_string_expr(expr["args"][0]):
            return None
        r = self._expr_to_whyml({"type": "Var", "name": recv}, local_refs,
                                invariant_ctx, subst)
        p = args[0]
        if method == "startswith":
            self._add_abstract_op(
                "val str_startswith_op (s: string) (prefix: string) : int\n"
                "    ensures { (result = 0) || (result = 1) }\n"
                "    ensures { (result = 1) <->\n"
                "      (String.length prefix <= String.length s /\\\n"
                "       String.substring s 0 (String.length prefix) = prefix) }")
            return f"(str_startswith_op {r} {p})"
        if method == "endswith":
            self._add_abstract_op(
                "val str_endswith_op (s: string) (suffix: string) : int\n"
                "    ensures { (result = 0) || (result = 1) }\n"
                "    ensures { (result = 1) <->\n"
                "      (String.length suffix <= String.length s /\\\n"
                "       String.substring s (String.length s - String.length suffix)\n"
                "         (String.length suffix) = suffix) }")
            return f"(str_endswith_op {r} {p})"
        # find — first-occurrence index, or -1
        self._add_abstract_op(
            "val str_find_op (s: string) (sub: string) : int\n"
            "    ensures { result >= -1 }\n"
            "    ensures { (result >= 0) ->\n"
            "      (result + String.length sub <= String.length s /\\\n"
            "       String.substring s result (String.length sub) = sub) }")
        return f"(str_find_op {r} {p})"

    def _call_named_builtins(self, expr: Dict[str, Any], args: List[str],
                             func_name: str, local_refs: Optional[Set[str]] = None,
                             invariant_ctx: bool = False,
                             subst: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Named builtins and built-in-method idioms: len / min / max / string-predicate
        methods / isinstance / set / sorted / any / all / dict / list / join /
        str|repr|int|bool|abs / sum / hasattr. Returns the WhyML string, or None to fall
        through to the generic call path. (Extracted verbatim from `_handle_call_expr`.)"""
        # no-more-int-3 A1 T1.2 (param-form) — `.get(k[, default])` on a
        # dict-typed Var receiver: faithful match against `Map.get`, NOT an
        # opaque `d_get_2` abstract op (which severs the result from the
        # receiver's contents). Returns the WhyML string, or None to fall
        # through to the generic dotted-call path (record-method `.get()` on
        # a class instance, a non-dict receiver, or a non-Var receiver).
        # typed-ir-for-b-ceiling.md §14: the `getattr(self, "<field>", <default>).get(k)`
        # idiom — the emitter's DEFENSIVE field access. The `.get`'s receiver is a
        # `getattr` Call, not a flat `self.<field>` name, so it would fall to the opaque
        # `get_1`. When the getattr names a DECLARED record dict/set field, rewrite the
        # receiver to `self.<field>` so `.get`/`.items`/… route to the real map field
        # (self-field dict reflection §12). Gated on @mutable_state → byte-identical.
        if (isinstance(func_name, str) and "." not in func_name
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _ga = self._getattr_self_field(expr.get("receiver"))
            if _ga and self._self_field_dict_nu(f"self.{_ga}") is not None:
                expr = dict(expr)
                expr["func"] = f"self.{_ga}.{func_name}"
                func_name = expr["func"]
                expr.pop("receiver", None)
        get_low = self._lower_dict_get_call(expr, args, func_name, local_refs,
                                            invariant_ctx, subst)
        if get_low is not None:
            return get_low
        if func_name == "len" and len(args) == 1:
            return self._handle_len_call(expr, args)
        if func_name in ("min", "max") and len(args) == 2:
            fn = "MinMax.min" if func_name == "min" else "MinMax.max"
            return f"({fn} {args[0]} {args[1]})"
        # strings-plan Stage 3: content-aware string methods on a simple `str`-typed
        # receiver. `s.startswith(p)`/`s.endswith(p)`/`s.find(sub)` get a substring-based
        # witness ensures (the receiver is lifted to an operand, unlike the opaque
        # baked-into-the-name predicates below, which apply to chained/non-str receivers).
        strm = self._content_string_method(expr, args, func_name, local_refs or set(),
                                           invariant_ctx, subst)
        if strm is not None:
            return strm
        # String predicate methods (`s.islower()`, `s.startswith(p)`, …) — model
        # as uninterpreted 0/1-valued ops, so a function that RETURNS the
        # predicate can prove `\result == 0 or \result == 1`. The value is not
        # related to the receiver (uninterpreted): design VCs on the predicate's
        # 0/1-ness or its control-flow consequence, not its concrete truth.
        if "." in func_name and func_name.rsplit(".", 1)[-1] in (
                "islower", "isupper", "isalpha", "isdigit", "isspace",
                "istitle", "isalnum", "isnumeric", "isdecimal",
                "isidentifier", "startswith", "endswith"):
            pname = whyml_ident(func_name.replace(".", "_")) + f"_{len(args)}"
            ens = "ensures { ((result = 0) || (result = 1)) }"
            if args:
                coerced = [self._coerce_to_int(a) for a in args]
                params = " ".join(f"(x{i}: int)" for i in range(len(args)))
                self._add_abstract_op(f"val {pname} {params} : int {ens}")
                return f"({pname} {' '.join(coerced)})"
            self._add_abstract_op(f"val {pname} () : int {ens}")
            return f"({pname} ())"
        # 07-0647-spec S3.2: a string predicate on a COMPUTED receiver
        # (`s[i].isdigit()`) arrives with a bare method `func` and the receiver in the
        # `receiver` field. The receiver MUST be passed as the first argument — emitting
        # a receiver-less `isdigit_0 ()` severs the result from the value tested (a silent
        # faithfulness violation). The op is still uninterpreted (0/1-valued).
        if (func_name in (
                "islower", "isupper", "isalpha", "isdigit", "isspace",
                "istitle", "isalnum", "isnumeric", "isdecimal",
                "isidentifier", "startswith", "endswith")
                and expr.get("receiver") is not None):
            recv = self._expr_to_whyml(expr["receiver"], local_refs, invariant_ctx, subst)
            # `args` are ALREADY lowered WhyML strings (set by `_handle_call_expr`); re-lowering
            # them via `_expr_to_whyml` crashes on the string (`'str' has no attribute
            # to_dict`). Exposed by self-annotating `<computed>.endswith(...)` (e.g.
            # `val_ir["func"].endswith(".to_dict")`); the corpus has no computed-receiver
            # isX/startswith/endswith, so this is byte-identical there.
            all_args = [recv] + list(args)
            pname = whyml_ident(func_name) + f"_{len(all_args)}"
            ens = "ensures { ((result = 0) || (result = 1)) }"
            # Each operand keeps its real type (the receiver of `s[i].isdigit()` is a
            # `string` char, not an int) — declare per-arg type variables so the
            # uninterpreted predicate accepts any operand types.
            params = " ".join(f"(x{i}: 'a{i})" for i in range(len(all_args)))
            self._add_abstract_op(f"val {pname} {params} : int {ens}")
            return f"({pname} {' '.join('(' + a + ')' for a in all_args)})"
        if func_name == "isinstance" and len(expr.get("args", [])) == 2:
            # 07-1839 P4: faithful metatype resolution — `subtag (\typeof x) T` (decided
            # from Γ's τ; base types via the subtag relation; symbolic at the `Any` tail).
            # Supersedes the old opaque `isinstance_check`.
            return self._handle_isinstance(expr)
        if func_name == "getattr" and 2 <= len(expr.get("args", [])) <= 3:
            # `getattr(obj, name[, default])` — attribute access on an arbitrary object.
            # Sound lowering (additive; previously fell through to an opaque `getattr_N`
            # abstract val that mismatched on record-typed `self`):
            #  • If `obj` is a Var of a known record type and `name` is a string literal
            #    matching a declared field → emit the genuine record field access
            #    `obj.<field>` (lets `\result == self.f` postconditions prove).
            #  • Otherwise (the dynamic-config case `getattr(self, "_x", {})` where
            #    `_x` isn't a declared field) → emit the `default` argument directly.
            #    getattr DOES return default for an absent attribute, so this is sound;
            #    the actual runtime value is opaque to the prover (fails-safe: any
            #    contract depending on the real value fails to prove, never proves false).
            return self._lower_getattr(expr, args, local_refs, invariant_ctx, subst)
        if func_name in ("set", "frozenset") and len(args) == 0:
            # Body set: same `map int (option int)` model as body dicts.
            # Sets store `Some 0` for "present" keys, `None` for absent.
            return "(const (None: option int))"
        _cf5_ms = (getattr(self, "_current_self_type", None)
                   in getattr(self, "_mutable_state_classes", set()))
        if (func_name in ("set", "frozenset") and len(args) == 1 and _cf5_ms
                and expr.get("args") and isinstance(expr["args"][0], dict)
                and expr["args"][0].get("type") == "Call"
                and self._call_returns_seq_string(expr["args"][0].get("func", ""))):
            # item34.md CF5: `set(<seq string collection>)` is the same list (dedup unmodelled).
            return args[0]
        if (isinstance(func_name, str) and func_name.endswith(".get") and len(args) == 2
                and _cf5_ms and expr.get("args") and len(expr["args"]) == 2
                and isinstance(expr["args"][1], dict)
                and expr["args"][1].get("type") in ("ArrayLit", "ListLit", "List")
                and not self._is_emit_ir_expr(
                    {"type": "Var", "name": func_name[:-len(".get")]})):
            # item34.md CF5: `<handler>.get("body", [])` — list-default on a NON-emit_ir handler
            # dict → `array int` STMT-LIST (the `list_comp_stmts` node model consumed by
            # `find_assigned_vars`/`_stmts_to_whyml`). GATED off emit_ir receivers so
            # `val_ir.get("elts",[])` keeps its int-model `.get` path.
            _grecv = whyml_ident(func_name.replace(".", "_"))
            self._add_abstract_op(f"val {_grecv}_arr (k: string) : array int")
            return f"({_grecv}_arr {args[0]})"
        if (isinstance(func_name, str) and func_name.endswith(".get") and len(args) == 1
                and _cf5_ms and expr.get("args") and isinstance(expr["args"][0], dict)
                and expr["args"][0].get("type") == "String"
                and not self._is_emit_ir_expr(
                    {"type": "Var", "name": func_name[:-len(".get")]})):
            # item34.md CF5: `<handler>.get("exc_type")` — 1-arg string-key `.get` on a
            # non-emit_ir handler dict reads a string scalar field.
            _grecv = whyml_ident(func_name.replace(".", "_"))
            self._add_abstract_op(f"val {_grecv}_str (k: string) : string")
            return f"({_grecv}_str {args[0]})"
        if func_name == "sorted" and len(args) == 1:
            # item34.md CF5: `sorted(<seq string>)` → `seq string` (`sorted_seq`); the name
            # collections are seq. Dispatch on the arg being a seq-string local.
            _sa = expr.get("args", [{}])[0]
            if (_cf5_ms and isinstance(_sa, dict) and _sa.get("type") == "Var"
                    and _sa.get("name") in getattr(self, "_seq_locals", set())
                    and getattr(self, "_seq_value_types", {}).get(_sa.get("name")) == "string"):
                self._add_abstract_op("val sorted_seq (a: seq string) : seq string")
                return f"(sorted_seq !{whyml_ident(_sa['name'])})"
            # cleared-array.md S5 (spike-proven, S0-bis): `sorted(a)` over an
            # `array int` returns a permuted, sorted array with the SAME length.
            # The three facts are DEFINITIONAL `ensures` on the abstract `val`
            # (discharged where `sorted` is USED, NOT a global axiom):
            #   * `Array.length result = Array.length a`
            #   * adjacent sortedness — the exact formula `\is_sorted(result)`
            #     lowers to, so a driver's `\is_sorted(result)` matches directly;
            #   * `permut result a` — the SAME uninterpreted predicate
            #     `\permutation(result, a)` lowers to (arg order result,a), so a
            #     driver's `\permutation(result, a)` matches directly.
            # sortedness + permut + equal-length is satisfiable (a sorted
            # permutation always exists) → no vacuity; adding ensures is
            # monotone → cannot regress a prior opaque proof.
            self._add_abstract_op("predicate permut (a: array int) (b: array int)")
            self._add_abstract_op(
                "val sorted_1 (a: array int) : array int\n"
                "    ensures { Array.length result = Array.length a }\n"
                "    ensures { forall _si : int. 0 <= _si < Array.length result - 1 ->\n"
                "                result[_si] <= result[_si + 1] }\n"
                "    ensures { permut result a }")
            return f"(sorted_1 {self._array_coerce_arg(args[0])})"
        if func_name in ("any", "all") and len(args) == 1:
            # `any(iterable)` / `all(iterable)` over an array — abstract.
            # Unsupported iterable shapes (generator expressions etc.) get
            # dropped to `0` at the IR level; coerce that to an array
            # placeholder so the abstract val type-checks.
            self._add_abstract_op(
                f"val {func_name}_1 (a: array int) : bool")
            return f"({func_name}_1 {self._array_coerce_arg(args[0])})"
        if func_name == "dict" and len(args) == 0:
            # Body dict: empty `map int (option int)`. Parallel to
            # `\empty_map` (`_handle_map_empty_expr`).
            return "(const (None: option int))"
        if (func_name in ("defaultdict", "Counter", "OrderedDict")
                and func_name not in self._record_types):
            # collections-plan: the dict-family reduces to the empty
            # `map int (option int)`. The factory (`defaultdict(int)`) or
            # iterable (`Counter([...])`) arg is dropped — the missing-key
            # default IS the model's None→0, and a seeded iterable is modelled
            # as empty (a sound under-approximation: content that depends on
            # the seed fails to prove, never proves falsely). `OrderedDict`
            # insertion order is not modelled. The `not in _record_types` guard
            # lets a user-defined/imported class of the same name (e.g. corpus
            # 0441's `Counter`) fall through to `_call_record_constructor`.
            return "(const (None: option int))"
        if func_name == "list" and len(args) <= 1:
            # `list(X)` where X already lowered to an `array int` expression
            # (e.g. `list(reversed(xs))`) is the identity — pass it through.
            if args and args[0].lstrip("(").startswith(
                    ("array_rev ", "Array.", "array_slice ", "array_copy ")):
                return args[0]
            # `list(iterable)` semantics depend on the surrounding return
            # type. In a `List[T] -> array int` context, emit an abstract
            # array-returning val so the result type-checks at the
            # function boundary. Otherwise keep the legacy `int -> int`
            # shape (used as a counter/length hash in body-int contexts —
            # eg. `list(A) + list(B)` for Python list concatenation).
            if self._func_return_type == "array int":
                self._add_abstract_op("val list_new_arr (x: int) : array int")
                return f"(list_new_arr {args[0] if args else '0'})"
            self._add_abstract_op("val list_new (x: int) : int")
            return f"(list_new {args[0] if args else '0'})"
        if func_name in ("bytes", "bytearray") and len(args) <= 1:
            # 07-1321 S1: faithful bytes/bytearray construction. A bytes buffer is an
            # `array int` (no-more-int doctrine), and the constructor is LENGTH- and
            # ELEMENT-preserving so byte-packing functions can prove `\length(\result)`
            # and `\result[i]` postconditions — not merely type-correct. The argument
            # already lowers to an `array int` expression (array literal or array-typed
            # local), so it is passed through directly (NOT `_array_coerce_arg`, which
            # would clobber a `(let _alit = Array.make …)` literal to a placeholder).
            ctor = func_name
            if args:
                self._add_abstract_op(
                    f"val {ctor}_new (x: array int) : array int\n"
                    f"    ensures {{ Array.length result = Array.length x }}\n"
                    f"    ensures {{ forall i:int. 0 <= i < Array.length x -> "
                    f"result[i] = x[i] }}")
                # L2 (os-bodyvc-spec): a seq-promoted local (`parts = []; parts += …`) passed to
                # `bytes()` must materialize seq→array — `bytes_new` expects `array int`, the seq is
                # `seq int` (the `@rho` error). Reuses the return-arr materialize bridge, now at a
                # call-arg boundary (it already covers return boundaries).
                arg0 = self._materialize_if_seq(args[0], expr.get("args", [{}])[0])
                return f"({ctor}_new {arg0})"
            self._add_abstract_op(
                f"val {ctor}_empty () : array int\n"
                f"    ensures {{ Array.length result = 0 }}")
            return f"({ctor}_empty ())"
        if func_name == "json_mirror" and len(args) == 1:
            # no-more-int A4: `json_mirror(x)` over a recursive `#@ datatype Json`
            # is an abstract `json → json` op (`val function` — program-callable
            # AND constrainable by a logic axiom). The imported inductive lemma
            # `mirror_involution : forall x. json_mirror (json_mirror x) = x`
            # (proved by structural induction in Rocq/Lean) discharges
            # `mirror(mirror(x)) == x` — testing the bridge on an INDUCTIVE
            # property over a recursive datatype (vs the flat 0537–0539).
            self._add_abstract_op("val function json_mirror (x: json) : json")
            return f"(json_mirror {args[0]})"
        if func_name == "reversed" and len(args) == 1:
            # no-more-int A2b Gap 5: `reversed(xs)` models the reversed sequence
            # as an abstract `array int` op `array_rev` (a `val function` — both
            # program-callable and constrainable by a logic axiom). The
            # `permut (array_rev s) s` framing lemma (imported via `#@ proof`)
            # is what proves `\permutation(reversed(xs), xs)`; uncited, it stays
            # an opaque reversal. `list(reversed(xs))` passes the array through.
            self._add_abstract_op(
                "val function array_rev (a: array int) : array int")
            return f"(array_rev {self._array_coerce_arg(args[0])})"
        if func_name == "join" and len(args) == 1:
            return self._handle_join_call(expr, args, local_refs, invariant_ctx, subst)
        if func_name == "hash" and len(args) == 1:
            # G2 strings: `hash(s)` of a string routes to the existing `str_hash_op`
            # (an uninterpreted `string -> int`) — yielding an int usable as a dict/set
            # key, over a real Why3 string (no int-coercion). A non-string `hash(x)` keeps
            # the generic call fallback below.
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if self._is_string_expr(arg_ir):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                return f"(str_hash_op {args[0]})"
        # 10-2300-spec-5: the `ord`/`chr` char<->int bridge. Handled here — BEFORE the
        # generic unannotated-callee path (which would declare `val ord_1 (x: int) : int`
        # and mis-type the 1-char STRING arg of `ord(name[i])`). `ord_op`/`chr_op` are
        # total abstract vals pinned by `string.Char`'s `code`/`chr`/`get` (no axiom).
        if func_name == "ord" and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if self._is_string_expr(arg_ir):
                # string-codec Phase A': context-dependent lowering. In a CONTRACT
                # (logic context) `ord` MUST lower to the pure `string.Char` logic
                # form — `val ord_op` is a PROGRAM symbol and cannot appear in a
                # `requires`/`ensures`/axiom. In a body keep `ord_op` (a body cannot
                # apply a logic `function`); the two agree by `ord_op`'s ensures.
                # `args[0]` is the lowered 1-char string (e.g. `(str_sub_op name i 1)`).
                if self._in_spec:
                    # string-codec Phase A': `ord(s[i])` — the dominant codec form — must
                    # lower to `Char.code (Char.get s i)` DIRECTLY, not via the
                    # `Char.get (String.substring s i 1) 0` detour. The two are equal by
                    # `substring_get`, but the detour leaves the encoding precondition
                    # syntactically unequal to `field_to_str_round_trip`'s antecedent, so
                    # the axiom never instantiates and SMT falls back to extensionality on
                    # the string-equality goal → OOM (measured). The direct form makes the
                    # axiom apply in O(1) (~19k steps, Valid).
                    if (arg_ir.get("type") == "Subscript"
                            and self._is_string_expr(arg_ir.get("value", {}))):
                        base = self._expr_to_whyml(
                            arg_ir["value"], local_refs or set(), invariant_ctx, subst)
                        idx = self._expr_to_whyml(
                            arg_ir["index"], local_refs or set(), invariant_ctx, subst)
                        return f"(Char.code (Char.get {base} {idx}))"
                    return f"(Char.code (Char.get {args[0]} 0))"
                # BODY: `ord(s[i])` lowers to a dedicated `char_code_at s i` val whose
                # ensures is the SAME logic form a contract uses (`Char.code (Char.get
                # s i)`), NOT `ord_op (str_sub_op s i 1)`. The latter routes through
                # `String.substring`, so an encode loop's invariant `out[j] == Char.code
                # (Char.get name j)` only matches the assigned value via a `substring_get`
                # bridge that E-match-explodes (OOM, measured). The direct form matches
                # the invariant atom-for-atom — the body twin of the Phase A' spec rule.
                if (arg_ir.get("type") == "Subscript"
                        and self._is_string_expr(arg_ir.get("value", {}))):
                    base = self._expr_to_whyml(
                        arg_ir["value"], local_refs or set(), invariant_ctx, subst)
                    idx = self._expr_to_whyml(
                        arg_ir["index"], local_refs or set(), invariant_ctx, subst)
                    self._add_abstract_op(
                        "val char_code_at (s: string) (i: int) : int\n"
                        "    ensures { 0 <= result < 256 }\n"
                        "    ensures { result = Char.code (Char.get s i) }")
                    return f"(char_code_at {base} {idx})"
                self._add_abstract_op(
                    "val ord_op (c: string) : int\n"
                    "    ensures { 0 <= result < 256 }\n"
                    "    ensures { result = Char.code (Char.get c 0) }")
                return f"(ord_op {args[0]})"
            # non-string `ord(x)`: fall through (return None) — keep current behaviour.
        if func_name == "chr" and len(args) == 1:
            # string-codec Phase A': same context split as `ord` (logic form in a
            # contract, program `chr_op` in a body).
            if self._in_spec:
                return f"((Char.chr {args[0]}).contents)"
            self._add_abstract_op(
                "val chr_op (n: int) : string\n"
                "    ensures { String.length result = 1 }\n"
                "    ensures { result = (Char.chr n).contents }")
            return f"(chr_op {args[0]})"
        if func_name in ("str", "repr", "format", "int", "bool", "abs") and len(args) == 1:
            arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
            if arg_ir.get("type") == "Number" and func_name in ("int", "abs"):
                val = arg_ir.get("value")
                if isinstance(val, (int, float)):
                    return str(int(val) if func_name == "int" else abs(int(val)))
            if func_name == "int":
                # typed-ir §18: `int(<str>)` (e.g. `int(ghost_type[-1])`) is a genuine
                # str→int conversion — an abstract `str_to_int` — not the int-identity.
                # Fires only for a string arg → byte-identical (an int arg is identity).
                if not self._in_spec and self._is_string_expr(arg_ir):
                    self._add_abstract_op("val str_to_int (s: string) : int")
                    return f"(str_to_int {args[0]})"
                return args[0]
            # G2 strings: `str(s)` / `format(s)` (no spec) of a string is the identity —
            # the same Why3 string, faithfully (mirrors the int identity above). `repr(s)`
            # is NOT identity (it adds quotes), so it is handled separately (str_repr_op).
            if func_name in ("str", "format") and self._is_string_expr(arg_ir):
                return args[0]
            # G2 strings: `repr(s)` of a string is an abstract string-valued op. Its content
            # transform is NOT modeled — Python adds 2 quotes ONLY for quote/escape-free
            # strings, so a `+2` *equality* length law would be UNSOUND. The only sound,
            # faithful length fact is the lower bound: `repr` of any str always carries at
            # least the two surrounding quote characters, so `length result >= 2`. No false
            # postcondition is emitted.
            if func_name == "repr" and self._is_string_expr(arg_ir):
                self._add_abstract_op(
                    "val str_repr_op (s: string) : string\n"
                    "    ensures { String.length result >= 2 }")
                return f"(str_repr_op {args[0]})"
            wf = whyml_ident(func_name)
            self._add_abstract_op(f"val {wf}_conv (x: int) : int")
            return f"({wf}_conv {args[0]})"
        if func_name == "sum" and len(args) == 1:
            result = self._handle_sum_call(expr)
            if result:
                return result
        if func_name == "hasattr":
            a0 = args[0] if args else "0"
            a1 = self._coerce_str_arg(args[1] if len(args) > 1 else "0")
            self_type = self._current_self_type
            if a0 == "self" and self_type:
                op = f"hasattr_check_{self_type}"
                self._add_abstract_op(f"val {op} (x: {self_type}) (a: int) : bool")
            else:
                op = "hasattr_check"
                self._add_abstract_op("val hasattr_check (x: int) (a: int) : bool")
            return f"({op} {a0} {a1})"
        if func_name == "exec":
            # 07-1839 P5a': a dynamic `exec` is a worst-case mutator (rev4 §8.4.2). In a
            # frame-checked model (typed/store) it WRITES the heap, so a narrow `assigns`
            # (e.g. `\nothing` → `ensures !heap = old !heap`) correctly fails — closing the
            # frame hole. In the value-semantic model `assigns` is not frame-checked, so an
            # opaque unit suffices (scope havoc is handled in P5a). Constant splice = P5b.
            code = args[0] if args else "0"
            if not self._value_semantic:
                hv = self._heap_var
                self._add_abstract_op(f"val exec_havoc (code: 'a) : unit writes {{ {hv} }}")
                return f"(exec_havoc {code})"
            self._add_abstract_op("val exec_stmt (code: 'a) : unit")
            return f"(exec_stmt {code})"
        if func_name in ("literal_eval", "ast.literal_eval") and len(expr.get("args", [])) == 1:
            # 07-1839 P5c: `literal_eval` of a CONSTANT literal is compile-time-knowable —
            # evaluate it with host `ast.literal_eval` (the source of truth) and emit the
            # ACTUAL value with its true type (faithful, rev4 §8.3). int/str handled; other
            # types (list/dict/float/bool) fall through to the opaque dynamic stub for now.
            arg0 = expr["args"][0]
            if isinstance(arg0, dict) and arg0.get("type") == "String":
                import ast as _hostast
                try:
                    v = _hostast.literal_eval(arg0.get("value", ""))
                    if isinstance(v, bool):
                        v = None  # defer bool (context-dependent true/false vs 1/0)
                    if isinstance(v, int):
                        return f"(- {abs(v)})" if v < 0 else str(v)
                    if isinstance(v, str):
                        return self._whyml_string_literal(v)
                except (ValueError, SyntaxError):
                    pass  # not a valid literal → opaque
            self._add_abstract_op("val literal_eval_op (s: 'a) : int")
            return f"(literal_eval_op {args[0] if args else '0'})"
        return None

    # ── 07-1839 P4: metatype tags + \subtag + isinstance ──────────────────────
    _METATYPE_TAGS = {"int": "tag_int", "bool": "tag_int", "str": "tag_str",
                      "float": "tag_float", "list": "tag_list", "List": "tag_list",
                      "dict": "tag_dict", "Dict": "tag_dict", "set": "tag_dict",
                      "frozenset": "tag_dict", "object": "tag_object"}

    # Literal int values for the on-demand `tag_*` logic functions (see
    # `_emit_metatype_tags`). In PROGRAM context Why3 rejects references to
    # logic `function` symbols ("Logical symbol tag_int is used in a non-ghost
    # context"), so `isinstance` lowered to a runtime int comparison inlines
    # these literals instead of naming the ghost `tag_*` functions.
    _TAG_LITERAL = {"tag_int": 0, "tag_str": 1, "tag_float": 2, "tag_list": 3,
                    "tag_dict": 4, "tag_record": 5, "tag_variant": 6,
                    "tag_object": 99}

    def _emit_metatype_tags(self) -> None:
        """Emit the tag constants + the `subtag` relation (P0-validated). Decision A:
        no `tag_bool` — bool collapses to `tag_int` (Γ has `τ(bool)=int`). subtag is
        reflexive + `b = object`; on-demand, so non-introspecting files stay identical."""
        for nm, v in (("tag_int", 0), ("tag_str", 1), ("tag_float", 2), ("tag_list", 3),
                      ("tag_dict", 4), ("tag_record", 5), ("tag_variant", 6),
                      ("tag_object", 99)):
            self._add_abstract_op(f"function {nm} : int = {v}")
        # `99` is `tag_object` inlined: the abstract-op block is emitted alphabetically,
        # so `subtag` must not reference `tag_object` by name (it would sort before it).
        # The `tag_*` functions are used only in goals (after all decls), so they are fine.
        self._add_abstract_op("predicate subtag (a b: int) = a = b \\/ b = 99")

    def _tag_of_type(self, t_name: str) -> str:
        """Tag for a *type name* (the 2nd arg of isinstance / a class / datatype).
        None ⇒ unknown target type (fully uninterpreted)."""
        if not t_name:
            return ""
        if t_name in self._METATYPE_TAGS:
            return self._METATYPE_TAGS[t_name]
        if t_name.lower() in getattr(self, "_record_types", {}):
            return "tag_record"
        if t_name in getattr(self, "_variant_types", {}):
            return "tag_variant"
        return ""

    def _tag_of_value(self, x_ir: Dict[str, Any]) -> str:
        """Tag of a *value* from Γ's τ (decision B: only a stable, concrete τ decides;
        `Any`/unstable/non-var → a free symbolic tag via `typeof_op`, so introspection on
        it stays unknown — never a wrong-decided)."""
        name = x_ir.get("name") if isinstance(x_ir, dict) and x_ir.get("type") == "Var" else None
        tag = self._tag_of_type(getattr(self, "_current_symbol_table", {}).get(name)) if name else ""
        if tag:
            return tag
        self._add_abstract_op("val function typeof_op (n: int) : int")
        return f"(typeof_op {sum(ord(c) for c in name) if name else 0})"

    def _union_none_ctor_for(self, x_ir: Dict[str, Any]) -> Optional[str]:
        """typing-engagement ty1 C5 — if `x_ir` is a Var whose symbol-table type
        is a synthesized `_union_*` variant that has a nullary `Arm_*_None`
        constructor, return that constructor name (so `x is None` lowers to a
        constructor check). Else None (caller falls back to `x = 0`)."""
        if not isinstance(x_ir, dict) or x_ir.get("type") != "Var":
            return None
        name = x_ir.get("name")
        symtype = getattr(self, "_current_symbol_table", {}).get(name)
        if not symtype or not isinstance(symtype, str) or not symtype.startswith("_union_"):
            return None
        vinfo = getattr(self, "_variant_types", {}).get(symtype)
        if not vinfo:
            return None
        for ctor_name, ctor in vinfo.get("constructors", {}).items():
            if ctor.get("arity") == 0 and "None" in ctor_name:
                return ctor_name
        return None

    def _handle_isinstance(self, expr: Dict[str, Any]) -> str:
        """`isinstance(x, T)` → `subtag (\\typeof x) T` (decision: \\subtag, not ==, so a
        base type like `object` decides true and a leaf≠leaf decides false). Decided when
        x has a concrete τ; symbolic at the `Any` tail; fully uninterpreted if T is an
        unknown type."""
        args_ir = expr.get("args", [])
        t_name = args_ir[1].get("name") if isinstance(args_ir[1], dict) else None
        t_tag = self._tag_of_type(t_name)
        if not t_tag:
            self._add_abstract_op("val isinstance_op (x: int) (t: int) : bool")
            return "(isinstance_op 0 0)"
        self._emit_metatype_tags()
        # In program (non-spec) context, `subtag` and the `tag_*` logic functions
        # are ghost symbols Why3 rejects inside an `if`/`while` condition
        # ("Logical symbol subtag/tag_int is used in a non-ghost context").
        # Lower to a runtime int equality on the value's type-tag discriminant,
        # inlining the tag's literal int on BOTH sides: `(<typeof x literal or
        # typeof_op call> = <T's tag literal>)` is a plain int `=` producing a
        # bool accepted in program `if`. In spec context the predicate form is
        # kept (it carries the sub-typing relation `a = b \/ b = 99`, exercising
        # the `object` base-type decision per corpus 0632).
        if not getattr(self, "_in_spec", False):
            lhs = self._tag_of_value(args_ir[0])
            if lhs in self._TAG_LITERAL:
                lhs = str(self._TAG_LITERAL[lhs])
            return f"({lhs} = {self._TAG_LITERAL[t_tag]})"
        return f"(subtag {self._tag_of_value(args_ir[0])} {t_tag})"

    def _lower_dict_get_call(self, expr: Dict[str, Any], args: List[str],
                              func_name: str, local_refs: Optional[Set[str]],
                              invariant_ctx: bool,
                              subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `d.get(k[, default])` on a dict-typed Var receiver to a
        faithful WhyML `match Map.get <recv> <k> with | Some v_ -> v_ |
        None -> <default> end`. The receiver must be a SIMPLE Var bound to a
        dict-typed parameter or body-local — record-field dict receivers
        (`self.f.get(...)`) and computed receivers fall through to the
        generic dotted-call path (their κ is not tracked in
        `_dict_key_types`, so a faithful lowering could not type-check).

        WhyML `Map.get` is total (returns `None` for an absent key), so —
        unlike the subscript read `d[k]` — NO `assert { Map.get d k <> None }`
        is emitted: `dict.get` is the missing-key-tolerant form, and the
        `None -> default` arm is reachable (the body VC reflects this, so
        an `ensures \result == <literal>` claim about an arbitrary dict's
        value remains honestly unprovable — the faithful model, not a
        trusted lie)."""
        # subscript-receiver .get projection: `a[i].get("name")` — the receiver is an emit_ir
        # EXPRESSION (an array element `a[i]`, not a dotted Var), carried in the Call's `receiver`
        # field with `func == "get"`. Project over the lowered receiver (kind_of/name_of/…). Must run
        # BEFORE the `"." not in func_name` bail (func_name is bare "get" here). @mutable_state /
        # emit_ir-gated (`_is_emit_ir_expr` is False otherwise) → byte-identical for the corpus.
        if func_name == "get":
            _rcv = expr.get("receiver")
            if isinstance(_rcv, dict) and self._is_emit_ir_expr(_rcv):
                _kir = (expr.get("args") or [{}])[0]
                if isinstance(_kir, dict) and _kir.get("type") == "String":
                    _k = _kir.get("value")
                    # an element's `.get("value")` reads its SCALAR string (a leaf String/Number
                    # node's value, e.g. `args[1]["value"]` = the getattr field name) → value_of,
                    # not the sub-node svalue_of that `_EMIT_IR_PROJ["value"]` picks for chaining.
                    _proj = "value_of" if _k == "value" else _EMIT_IR_PROJ.get(_k)
                    if _proj:
                        _rv = self._expr_to_whyml(_rcv, local_refs or set(),
                                                  invariant_ctx, subst)
                        return f"({_proj} {_rv})"
        if "." not in func_name:
            return None
        recv, method = func_name.rsplit(".", 1)
        if method != "get":
            return None
        if len(args) not in (1, 2):
            return None
        # §26: `X.get(k)` where X aliases a self dict-field → `self.<field>.get(k)`.
        _alias = self._alias_self_field(recv)
        if _alias:
            recv = _alias
            func_name = f"{_alias}.get"
        # todict-reflection-plan.md R1: `d` aliases `node.to_dict()` — route
        # `d.get(key)` to the node's TYPED field (no dict materialized).
        _recv_dotted = getattr(self, "_todict_aliases", {}).get(recv)
        if _recv_dotted is not None:
            _kir = (expr.get("args") or [{}])[0]
            if isinstance(_kir, dict) and _kir.get("type") == "String":
                _proj = self._todict_emit_ir_projection(_recv_dotted, _kir.get("value"), local_refs, invariant_ctx, subst)
                if _proj is not None: return _proj
                return self._expr_to_whyml(
                    self._todict_routed_ir(_recv_dotted, _kir.get("value")),
                    local_refs or set(), invariant_ctx, subst)
        # typed-ir-for-b-ceiling.md B-C3: reflection over an `emit_ir`-typed receiver —
        # `node.get("type")` → `(kind_of node)`, `"name"`/`"attr"` → `(name_of node)`,
        # `"value"` → `(value_of node)`, `"object"` → `(object_of node)`. A total
        # projection over the sum, not a map read. Fires only when `recv` is emit_ir
        # (a param/local ExprIR); gated by the ExprIR tags → byte-identical.
        _recv_ir = {"type": "Var", "name": recv}
        if self._is_emit_ir_expr(_recv_ir):
            _kir = (expr.get("args") or [{}])[0]
            if isinstance(_kir, dict) and _kir.get("type") == "String":
                _proj = _EMIT_IR_PROJ.get(_kir.get("value"))
                if _proj:
                    _rv = self._expr_to_whyml(_recv_ir, local_refs or set(),
                                              invariant_ctx, subst)
                    return f"({_proj} {_rv})"
        symtab = getattr(self, "_current_symbol_table", {}) or {}
        recv_symtype = symtab.get(recv)
        is_dict = (recv_symtype == "dict"
                   or recv in getattr(self, "_dict_locals", set()))
        # self-field-dict-reflection: `self.<dict-field>.get(key)` reads the declared
        # record dict/set field via `Map.get self.<field> …` (not an opaque abstract).
        # `_self_field_dict_nu` returns the field's value type when `recv` is a
        # `dict`/`set`-typed record field, else None. typed-ir-for-b-ceiling.md §12.
        _field_nu = self._self_field_dict_nu(recv)
        if _field_nu is not None:
            _o, _f = recv.rsplit(".", 1)
            recv_whyml = self._expr_to_whyml(
                {"type": "FieldGet", "object": _o, "field": _f},
                local_refs or set(), invariant_ctx, subst)
            _kir = (expr.get("args") or [{}])[0]
            _kstr = isinstance(_kir, dict) and _kir.get("type") == "String"
            if not self._in_spec and self._is_string_expr(_kir if isinstance(_kir, dict) else {}):
                self._add_abstract_op("val str_hash_op (s: string) : int")
                k = f"(str_hash_op {args[0]})"
            else:
                k = self._coerce_to_int(args[0])
            # #15: for a NESTED-collection value (`seq _`/`map _`), the explicit `[]`/`{}` default
            # is a type-generic empty that lowers to the WRONG shape (`array int` for `[]`); use the
            # ν-typed empty instead so the `None ->` arm matches the `Some v_` (inner seq/map).
            if (isinstance(_field_nu, str)
                    and _field_nu.startswith(("seq ", "map ", "array "))):
                default = self._dv_missing_default(_field_nu)
            else:
                default = args[1] if len(args) >= 2 else self._dv_missing_default(_field_nu)
            return (f"(match Map.get {recv_whyml} {k} "
                    f"with | Some v_ -> v_ | None -> {default} end)")
        if not is_dict:
            return None
        # Receiver WhyML: a body-local dict is a `ref` (reads deref via `!`);
        # a dict parameter is a plain value. `_handle_var_expr` produces the
        # correct form for each.
        recv_whyml = self._expr_to_whyml({"type": "Var", "name": recv},
                                         local_refs or set(),
                                         invariant_ctx, subst)
        kappa = getattr(self, "_dict_key_types", {}).get(recv)
        nu = getattr(self, "_dict_value_types", {}).get(recv)
        # Key: pass through unhashed when κ = string; int-coerce otherwise
        # (matches the body subscript read path's key handling).
        k = args[0] if kappa == "string" else self._coerce_to_int(args[0])
        # Default: the user-provided arg if present, else the ν-typed missing
        # placeholder (parallel to the subscript read's `None ->` arm).
        if len(args) >= 2:
            default = args[1]
        else:
            default = self._dv_missing_default(nu)
        return (f"(match Map.get {recv_whyml} {k} "
                f"with | Some v_ -> v_ | None -> {default} end)")

    def _lower_getattr(self, expr: Dict[str, Any], args: List[str],
                       local_refs: Set[str], invariant_ctx: bool,
                       subst: Optional[Dict[str, str]]) -> str:
        """Lower `getattr(obj, name[, default])` — see the `getattr` branch in
        `_handle_call_expr`. Record-field access when the field is statically known;
        else the default (sound under-approximation)."""
        args_ir = expr.get("args", [])
        obj_ir = args_ir[0]
        name_ir = args_ir[1] if len(args_ir) > 1 else {}
        default_ir = args_ir[2] if len(args_ir) > 2 else {"type": "Number", "value": 0}
        # Resolve `obj` to a known record-typed Var and `name` to a string literal.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            obj_name = obj_ir.get("name", "")
            st = getattr(self, "_current_symbol_table", {})
            obj_type = st.get(obj_name)
            if obj_type and obj_type.lower() in getattr(self, "_record_types", {}):
                rec_info = self._record_types[obj_type.lower()]
                fields = rec_info.get("fields", []) if isinstance(rec_info, dict) else []
                if isinstance(name_ir, dict) and name_ir.get("type") == "String":
                    attr = name_ir.get("value", "")
                    if attr in fields:
                        rec_lower = obj_type.lower()
                        return f"{whyml_ident(obj_name)}.{self._field_label(rec_lower, attr)}"
        # Dynamic-config / unknown-field path: emit the default. getattr returns
        # `default` for an absent attribute, so this is sound (the real runtime
        # value is opaque; any contract depending on it fails to prove).
        # For a NON-scalar default (dict/list/set literal) the lowered form is a
        # map/array, which would mismatch the enclosing local's int-typed `ref`
        # slot (first-assignment inference sees a `Call` RHS, not a collection
        # literal, so it can't promote the local to a dict/array). Coerce those
        # to an opaque `0` — the dict/list content is then unmodeled (a `.get`
        # chain on the result will not prove; fails-safe). A scalar int/bool
        # default passes through faithfully.
        if len(args_ir) <= 2:
            return "0"
        nt = default_ir.get("type") if isinstance(default_ir, dict) else ""
        if nt in ("DictLit", "ArrayLit", "SetLit", "Call"):
            return "0"
        return self._expr_to_whyml(default_ir, local_refs, invariant_ctx, subst)

    def _subst_params(self, ir: Any, arg_nodes: Dict[str, Any]) -> Any:
        """Deep-copy a value IR, replacing each `Var(param)` with its pre-lowered arg
        node (`RawWhyml`) — the IR-level value substitution used by parametrized record
        construction. Pure structural recursion over dict/list IR; leaves are returned
        as-is."""
        if isinstance(ir, dict):
            if ir.get("type") == "Var" and ir.get("name") in arg_nodes:
                return arg_nodes[ir["name"]]
            return {k: self._subst_params(v, arg_nodes) for k, v in ir.items()}
        if isinstance(ir, list):
            return [self._subst_params(x, arg_nodes) for x in ir]
        return ir

    def _call_record_constructor(self, args: List[str], func_name: str) -> Optional[str]:
        """`C(...)` for a known record type → a WhyML record literal with per-field,
        type-correct values. Returns None only if `func_name` is not a known record
        type. (Extracted from `_handle_call_expr`.)

        base_op.md Tier A — parametrized construction: when `C(a, b)` is called with
        args matching `__init__`'s formals, each scalar field whose `__init__` body
        set it from those params (`init_body`, captured by Module5) is initialised by
        substituting the actual args for the params; all other fields keep their
        type-correct default. A 0-arg `C()`, an arity mismatch, or a non-scalar /
        non-param-dependent field all fall back to the default witness (sound)."""
        if func_name not in self._record_types:
            return None
        rec_info = self._record_types[func_name]
        rec_lower = func_name.lower()
        field_types = rec_info.get("field_types", {})

        def _field_default(fn: str) -> str:
            # Per-type default so a driver constructing `C()` builds a
            # type-correct record. A list/array field defaults to an
            # `Array.make <len> 0` (len from field_defaults, captured by
            # Module5._array_init_size) so its `\length` invariant holds;
            # a dict/set field to the empty map; everything else to its
            # captured int (fallback 0).
            ft = field_types.get(fn, "int")
            if ft in ("list", "array"):
                return f"(Array.make {rec_info['defaults'].get(fn, 0)} 0)"
            if ft in ("dict", "set", "frozenset"):
                return "(const (None: option int))"
            return f"{rec_info['defaults'].get(fn, 0)}"

        # Parametrized overrides: map each param-initialised scalar field to its
        # arg-substituted value. Only when the call arity matches `__init__`. The
        # already-lowered arg strings are spliced in via `RawWhyml` IR nodes (a value
        # substitution — `subst` is a variable-RENAME map, not a value-injection one).
        init_map: Dict[str, str] = {}
        init_params = rec_info.get("init_params", [])
        init_body = rec_info.get("init_body", [])
        if args and init_params and len(args) == len(init_params):
            arg_nodes = {init_params[i]: {"type": "RawWhyml", "whyml": args[i]}
                         for i in range(len(init_params))}
            for ent in init_body:
                fn = ent["field"]
                # Only scalar (int-modelled) fields take a substituted value; a
                # list/dict/set field keeps its typed default (array/map construction
                # over a param is out of Tier-A scope).
                if field_types.get(fn, "int") in ("list", "array", "dict", "set", "frozenset"):
                    continue
                init_map[fn] = self._expr_to_whyml(
                    self._subst_params(ent["value"], arg_nodes), set())

        field_inits = "; ".join(
            f"{self._field_label(rec_lower, fn)} = {init_map.get(fn, _field_default(fn))}"
            for fn in rec_info["fields"]
        )
        return f"{{ {field_inits} }}"

    def _call_bytes_methods(self, args: List[str], func_name: str) -> Optional[str]:
        """Bytes-producing methods (`b.encode()`, `b.ljust()`, …) reach the generic path
        with no receiver dot in the IR func name. They return a byte buffer (`array int`),
        and any array-shaped operand (the receiver byte string, a slice) must stay
        `array int` so the result can flow into a `struct.pack('>...30s', …)` name field.
        Opaque — the byte content is not modeled. (Gap 5.) Returns None if not a bytes
        method. (Extracted from `_handle_call_expr`.)"""
        if func_name not in ("encode", "ljust", "rjust", "zfill"):
            return None
        n = len(args)
        arity_fn = f"{whyml_ident(func_name)}_{n}"
        _ARR = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
                "(struct_pack", "(encode_", "(ljust_", "(rjust_", "(zfill_",
                # 0442.md C1: a bytes literal (e.g. the `ljust(w, b'\\x00')` fill char)
                # lowers to `(let _alit = Array.make N v in …)` — an `array int`, not int.
                "(let _alit = Array.make")
        ptypes: List[str] = []
        cargs: List[str] = []
        for a in args:
            st = a.strip()
            is_arr = (any(st.startswith(p) for p in _ARR) or
                      st.lstrip("!").replace("_", "").isalnum() and
                      st.lstrip("!") in getattr(self, "_array_locals", set()))
            if is_arr:
                ptypes.append("array int")
                cargs.append(self._array_coerce_arg(a))
            else:
                ptypes.append("int")
                cargs.append(self._coerce_to_int(a))
        params = (" ".join(f"(x{i}: {t})" for i, t in enumerate(ptypes))
                  if n else "()")
        # 1009.md R2: `s.ljust(w[, fill])` / `rjust` / `zfill(w)` pad to AT LEAST
        # width `w` — Python returns the original when it is already longer — and `w`
        # is the first argument `x0`. Emit that length lower bound so a downstream
        # `\valid(name_bytes, 30)` (`Array.length >= 30`) discharges when fed a
        # `…ljust(30, b'\x00')`. (`encode`'s output length is genuinely unknown, so it
        # gets no bound: `>= 0` would be vacuous. Width must be an int operand.)
        length_ens = ""
        if func_name in ("ljust", "rjust", "zfill") and n >= 1 and ptypes[0] == "int":
            length_ens = "\n    ensures { Array.length result >= x0 }"
        self._add_abstract_op(f"val {arity_fn} {params} : array int{length_ens}")
        return f"({arity_fn} {' '.join(cargs) if cargs else '()'})"

    def _typeddict_field_access(self, value: Dict[str, Any],
                                index_ir: Dict[str, Any],
                                local_refs: Set[str],
                                invariant_ctx: bool,
                                subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `p["x"]` on a TypedDict-record-typed receiver to `p.x`.

        Per the two-plane spec §1.2 T5 and the core-agent hard rule
        (typing-global-impl.md §5, TY2): a string-literal subscript into a
        TypedDict-typed variable/field lowers to a record-field read. Returns
        None for non-TypedDict receivers OR a non-string-literal index (so the
        caller falls through to the existing array/dict/opaque paths — byte-
        identical for non-TypedDict drivers). The static plane is Interpreted
        (record-field read); the runtime plane is the plain-dict alias
        (Shimmed) — the runtime never sees this lowering (no blend)."""
        if index_ir.get("type") != "String":
            return None
        field_name = index_ir.get("value", "")
        if not isinstance(field_name, str) or not field_name:
            return None
        rec_name = None
        if value.get("type") == "Var":
            sym = getattr(self, "_current_symbol_table", {}).get(value.get("name", ""))
            if sym and sym in getattr(self, "_record_types", {}):
                if self._record_types[sym].get("is_typeddict"):
                    rec_name = sym
        if rec_name is None and value.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(value)
            if ft and ft in getattr(self, "_record_types", {}):
                if self._record_types[ft].get("is_typeddict"):
                    rec_name = ft
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        if field_name not in rec_info["fields"]:
            return None
        rec_lower = rec_info["whyml_name"]
        base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        return f"{base}.{self._field_label(rec_lower, field_name)}"

    def _typeddict_record_literal(self, expr: Dict[str, Any],
                                  local_refs: Set[str],
                                  invariant_ctx: bool,
                                  subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower a `DictLit` in a TypedDict construction context to a record
        literal `{ x = v0; y = v1 }` (per the two-plane spec §1.3 T8 and the
        core-agent hard rule).

        The construction context is detected from `_func_return_type` (a
        `return {"x":1,"y":2}` in a `-> Point` function): if the return type
        is a known TypedDict record's whyml_name, the literal is matched
        field-by-field against the record's declared fields (in declaration
        order) and each value is lowered. Returns None for non-TypedDict
        construction contexts (byte-identical fallback to the empty-map stub).
        Why3 type-checks each field's value against the declared field type
        natively (T8/T9)."""
        frt = getattr(self, "_func_return_type", "")
        if not frt:
            return None
        rec_name = None
        for name, info in getattr(self, "_record_types", {}).items():
            if info.get("whyml_name") == frt and info.get("is_typeddict"):
                rec_name = name
                break
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        rec_lower = rec_info["whyml_name"]
        keys = expr.get("keys", [])
        values = expr.get("values", [])
        # Build a key→value map (keys are String IR nodes per _py_expr_dict).
        kv: Dict[str, Dict[str, Any]] = {}
        for k, v in zip(keys, values):
            if isinstance(k, dict) and k.get("type") == "String":
                kv[k.get("value", "")] = v
        # T8/T9 (typeddict-twoplane-spec.md §1.3): every declared field must be
        # present (T9 — missing required key is a static error) AND no extra key
        # may be present (T9 — extra key is a static error). The default-filling
        # in the loop below is reserved for the `Point()` zero-arg construction
        # path (`_call_record_constructor`); the dict-literal path is a
        # fully-specified construction and must reject missing/extra keys.
        # GAP-001 (typing-engagement ty2): previously the missing field was
        # silently filled with its default, bypassing the T9 obligation.
        declared = set(rec_info["fields"])
        present = set(kv.keys())
        missing = [f for f in rec_info["fields"] if f not in present]
        extra = [k for k in present if k not in declared]
        if missing or extra:
            from errors import PyCSLSemanticError
            if missing:
                raise PyCSLSemanticError(
                    f"TypedDict construction is missing required key(s) "
                    f"{missing!r} (T9 / PEP 589 — a total=True TypedDict "
                    f"literal must provide every declared key).",
                    stage="whyml-emit")
            raise PyCSLSemanticError(
                f"TypedDict construction has extra key(s) "
                f"{extra!r} not declared on the TypedDict (T9 / PEP 589 — "
                f"a literal must not provide keys outside the declared set).",
                stage="whyml-emit")
        # Emit each declared field in declaration order. All declared fields
        # are present (missing/extra rejected above); each value is lowered
        # against its declared field type, and Why3 type-checks it natively
        # (T8 — typed construction).
        parts: List[str] = []
        for fname in rec_info["fields"]:
            v = kv.get(fname)
            val = self._expr_to_whyml(v, local_refs, invariant_ctx, subst)
            parts.append(f"{self._field_label(rec_lower, fname)} = {val}")
        return "{ " + "; ".join(parts) + " }"

    def _namedtuple_positional_access(self, value: Dict[str, Any],
                                      index_ir: Dict[str, Any],
                                      local_refs: Set[str],
                                      invariant_ctx: bool,
                                      subst: Optional[Dict[str, str]]) -> Optional[str]:
        """Lower `p[0]` on a NamedTuple-record-typed receiver to `p.<field at index 0>`.

        Per the two-plane spec §1.3 N5 and the core-agent hard rule
        (typing-global-impl.md §5, TY2): an integer-literal subscript into a
        NamedTuple-typed variable/field lowers to a record-field read of the
        field at that declaration index. Returns None for non-NamedTuple
        receivers OR a non-integer-literal index (so the caller falls through
        to the existing array/dict/opaque paths — byte-identical for non-
        NamedTuple drivers). The static plane is Interpreted (record-field
        read by index); the runtime plane is the plain-tuple alias (Shimmed) —
        the runtime never sees this lowering (no blend)."""
        if index_ir.get("type") != "Number":
            return None
        idx_val = index_ir.get("value")
        if not isinstance(idx_val, int) or idx_val < 0:
            return None
        rec_name = None
        if value.get("type") == "Var":
            sym = getattr(self, "_current_symbol_table", {}).get(value.get("name", ""))
            if sym and sym in getattr(self, "_record_types", {}):
                if self._record_types[sym].get("is_namedtuple"):
                    rec_name = sym
        if rec_name is None and value.get("type") in ("Attribute", "FieldGet"):
            ft = self._field_type_of(value)
            if ft and ft in getattr(self, "_record_types", {}):
                if self._record_types[ft].get("is_namedtuple"):
                    rec_name = ft
        if rec_name is None:
            return None
        rec_info = self._record_types[rec_name]
        fields = rec_info["fields"]
        if idx_val >= len(fields):
            return None
        field_name = fields[idx_val]
        rec_lower = rec_info["whyml_name"]
        base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        return f"{base}.{self._field_label(rec_lower, field_name)}"

    def _handle_subscript(self, node: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool = False, subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        value = expr["value"]
        index = self._expr_to_whyml(expr["index"], local_refs, invariant_ctx, subst)
        # B-C5: `<emit_ir>.get("args")[0]` → `arg0_of` (the Call's first arg node).
        _ar0 = self._emit_ir_args_recv_ir(expr.get("value", {}))
        if _ar0 is not None and index == "0":
            return (f"(arg0_of {self._expr_to_whyml(_ar0, local_refs or set(), invariant_ctx, subst)})")
        # B-C6: `<emit_ir>["elts"][i]` (i in 0,1) → `elt{i}_of` — a MkTuple element
        # sub-node, for ghost_assign's ghost-dict `+=` branch `val_ir["elts"][0/1]`.
        _elt = self._emit_ir_args_recv_ir(expr.get("value", {}), "elts")
        if _elt is not None and index in ("0", "1"):
            return (f"(elt{index}_of {self._expr_to_whyml(_elt, local_refs or set(), invariant_ctx, subst)})")
        # §26: subscript-form emit_ir projection `<emit_ir>["value"/"name"/"type"/…]` →
        # the projection (mirrors the `.get` B-C3 routing), for `arr["value"]["name"]`.
        _kidx = expr.get("index", {})
        if (isinstance(_kidx, dict) and _kidx.get("type") == "String"
                and self._is_emit_ir_expr(value)):
            # cf6.md M1.3: SUBSCRIPT `c["pattern"]` reads the pattern SUB-NODE (`svalue_of`),
            # whereas `.get("pattern")` reads its KIND string — same key, different meaning at
            # different nesting. So subscript "pattern" projects to a NODE, not `kind_of`.
            _kv = _kidx.get("value")
            # self-tcb-reduction T1.a: SUBSCRIPT `expr['object']` is the object NAME string
            # (`FieldGet.object: str`) — the name of the object sub-node (`name_of ∘ object_of`),
            # distinct from `.get("object")` (a node). The only un-trusted subscript-"object" user is
            # `_handle_field_get_expr` (`obj == "self"`, `f"{obj}.{field}"`).
            if _kv == "object":
                _rv = self._expr_to_whyml(value, local_refs or set(), invariant_ctx, subst)
                return f"(name_of (object_of {_rv}))"
            _proj = "svalue_of" if _kv == "pattern" else _EMIT_IR_PROJ.get(_kv)
            if _proj:
                return f"({_proj} {self._expr_to_whyml(value, local_refs or set(), invariant_ctx, subst)})"
        # §26: `X[k]` where X aliases a self dict-field → `Map.get self.<field> <k>` (the
        # getattr-bound-local read; `known_sizes[var_name]`). Mirrors the field-dict get.
        if isinstance(value, dict) and value.get("type") == "Var":
            _al = self._alias_self_field(value.get("name", ""))
            if _al:
                _fld = _al.split(".", 1)[1]
                _nu = self._self_field_dict_nu(_al)
                _recv = f"self.{self._field_label(getattr(self, '_current_self_type', None), _fld)}"
                _kir = expr.get("index", {})
                if not self._in_spec and self._is_string_expr(_kir):
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    _key = f"(str_hash_op {index})"
                else:
                    _key = self._coerce_to_int(index)
                _dflt = '""' if _nu == "string" else "0"
                return f"(match Map.get {_recv} {_key} with | Some _v -> _v | None -> {_dflt} end)"
        # faithful-string-op.md §3.4: `<string>.split(sep)[i]` / `.rsplit(sep,k)[i]` → the
        # i-th piece — a substring of the receiver (str_split_elem_op). Length law only;
        # content unmodeled, so `[0]`/`[1]`/`[-1]` share the op (the bound holds for any i).
        _sp = self._split_call_recv_sep(expr.get("value", {}))
        if _sp is not None and not self._in_spec:
            _rcv, _sep = _sp
            _rcvw = self._expr_to_whyml(_rcv, local_refs or set(), invariant_ctx, subst)
            _sepw = (self._expr_to_whyml(_sep, local_refs or set(), invariant_ctx, subst)
                     if _sep is not None else '" "')
            self._add_abstract_op(
                "val str_split_elem_op (s sep: string) (i: int) : string\n"
                "    ensures { String.length result <= String.length s }")
            return f"(str_split_elem_op {_rcvw} {_sepw} {index})"
        # typing-engagement ty2 / 29-1700-typing-spec-5 §2.2 T5: a string-literal
        # subscript `p["x"]` on a TypedDict-record-typed receiver lowers to a
        # record-field read `p.x` (the core-agent hard rule). Non-TypedDict
        # receivers and non-literal indices fall through unchanged
        # (byte-identical). The static plane is Interpreted (record-field read);
        # the runtime plane is the plain-dict alias (Shimmed) — no blend.
        td_access = self._typeddict_field_access(value, expr.get("index", {}),
                                                  local_refs, invariant_ctx, subst)
        if td_access is not None:
            return td_access
        # typing-engagement ty2 / 30-1700-typing-spec-6 §2.2 N5: an integer-
        # literal subscript `p[0]` on a NamedTuple-record-typed receiver lowers
        # to a record-field read of the field at that declaration index (the
        # core-agent hard rule). Non-NamedTuple receivers and non-literal
        # indices fall through unchanged (byte-identical). The static plane is
        # Interpreted (record-field read by index); the runtime plane is the
        # plain-tuple alias (Shimmed) — no blend.
        nt_access = self._namedtuple_positional_access(value, expr.get("index", {}),
                                                       local_refs, invariant_ctx,
                                                       subst)
        if nt_access is not None:
            return nt_access
        # 07-1705-rev4 P3/P5: element read of a seq-modelled list local is `Seq.get` —
        # BODY context only (in a contract a seq-promoted param is the array entry value).
        if (isinstance(value, dict) and value.get("type") == "Var"
                and value.get("name") in getattr(self, "_seq_locals", set())
                and not self._in_spec):
            base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)  # `!a`
            return f"(Seq.get {base} {index})"
        # strings-plan Stage 2: s[i] on a str is the 1-char substring String.substring s i 1
        # (Why3 strings have no char type; a character is a length-1 string). Reuses the
        # str_sub_op bridge whose length lemma gives String.length result = 1 under bounds.
        if self._is_string_expr(value):
            vstr = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
            if self._in_spec:
                return f"(String.substring {vstr} {index} 1)"
            self._add_abstract_op(
                "val str_sub_op (s: string) (lo len: int) : string\n"
                "    ensures { result = (String.substring s lo len) }\n"
                "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                " -> String.length result = len }")
            return f"(str_sub_op {vstr} {index} 1)"
        # 07-0903 W1: `a[i][k]` where `a` is a list/array of tuples — the inner `a[i]` is
        # a tuple value (`Array.get`), so destructure its k-th component. Must precede the
        # 2-D matrix detection below (which would otherwise read `a` as a `matrix`).
        if (value.get("type") == "Subscript"
                and value.get("value", {}).get("type") == "Var"
                and value["value"]["name"] in getattr(self, "_tuple_array_locals", {})):
            _ta = self._tuple_array_locals[value["value"]["name"]]
            try:
                _tk = int(index)
            except ValueError:
                _tk = -1
            if 0 <= _tk < _ta:
                _elem = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
                _bind = ", ".join(f"_r{_tk}_" if j == _tk else "_" for j in range(_ta))
                return f"(let ({_bind}) = {_elem} in _r{_tk}_)"
        # \result[i] on a tuple return → let-destructure
        if value.get("type") == "Result" and hasattr(self, "_current_tuple_arity"):
            arity = self._current_tuple_arity
            if arity and arity > 0:
                try:
                    idx = int(index)
                except ValueError:
                    idx = -1
                if 0 <= idx < arity:
                    names = [f"_r{k}_" if k != idx else f"_r{idx}_" for k in range(arity)]
                    bindings = ", ".join(
                        names[k] if k == idx else "_" for k in range(arity)
                    )
                    return f"(let ({bindings}) = result in _r{idx}_)"
        # 0442.md C2: `p[i]` on a tuple-typed local (`p = mk(x)` where `mk` returns a
        # tuple) → destructure, not the abstract `subscript_get (x:int)` (a type error
        # against the `(int, …)` tuple). Arity is tracked in `_ghost_tuple_vars`.
        if value.get("type") == "Var":
            _tarity = getattr(self, "_ghost_tuple_vars", {}).get(value.get("name", ""), 0)
            if _tarity and _tarity > 0:
                try:
                    _idx = int(index)
                except ValueError:
                    _idx = -1
                if 0 <= _idx < _tarity:
                    _bind = ", ".join(f"_r{_idx}_" if k == _idx else "_"
                                      for k in range(_tarity))
                    _base = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
                    return f"(let ({_bind}) = {_base} in _r{_idx}_)"
        # Detect 2D access: a[i][j] → Subscript(Subscript(Var(a), i), j)
        if (value.get("type") == "Subscript" and
                value.get("value", {}).get("type") == "Var" and
                value.get("value", {}).get("name") in getattr(self, "_array2d_params", set()) and
                value.get("value", {}).get("name") not in getattr(self, "_dict_locals", set())):
            base = value["value"]["name"]
            row = self._expr_to_whyml(value["index"], local_refs, invariant_ctx, subst)
            col = index
            return f"(get {base} {row} {col})"
        value_str = self._expr_to_whyml(value, local_refs, invariant_ctx, subst)
        # L0 (os-bodyvc-spec): `\result[i]` in a CONTRACT where the function returns `array int`
        # is a real `Array.get` (`result[i]`), not the opaque `subscript_get` — otherwise a value
        # postcondition over an array result (`\result[0]*256 + \result[1] == v`) can't even be
        # expressed, let alone proven. Spec context only (a logic term — no bounds-assert wrapper,
        # matching the hand-verified .mlw); opaque-typed reads still fall through to subscript_get.
        if (self._in_spec and value.get("type") == "Result"
                and getattr(self, "_func_return_type", "") == "array int"):
            return f"({value_str}[{index}])"
        # L0′ (challenging-the-plan §4.1): `self.<array-field>[i]` in a contract/class-invariant is a
        # real `Array.get`, not the opaque (and, in a class invariant, unbound) `subscript_get` — so a
        # data-refinement coupling invariant `ginode[n] == unpack(self.disk[…])` can be expressed.
        # Spec context only, logic term (no bounds-assert wrapper). Needs `_current_self_type` set
        # during class-invariant emission (preamble L0′ part 1) for `_field_type_of` to resolve.
        if (self._in_spec and value.get("type") in ("Attribute", "FieldGet")
                and self._field_type_of(value) in ("list", "tuple", "bytes", "bytearray")):
            return f"({value_str}[{index}])"
        if self._value_semantic:
            # A1-residual nested-map: `d[ko][ki]` — the inner read `d[ko]`
            # yields a `map κi (option νi)` (the outer dict's nested-map value),
            # so the outer `[ki]` is itself a `Map.get`, not the opaque
            # `subscript_get`. `value` here is the inner Subscript `d[ko]`;
            # `value_str` is its already-lowered map expression.
            if value.get("type") == "Subscript":
                _ib = value.get("value", {})
                _nu = (getattr(self, "_dict_value_types", {}).get(_ib.get("name", ""))
                       if isinstance(_ib, dict) and _ib.get("type") == "Var" else None)
                # nested-map.md: `self._nested_field[ko][ki]` — the inner base is a self dict-field
                # whose value_type is itself a `map …` (nested dict), so the outer `[ki]` reads that
                # inner map. Parallel to the body-dict `d[ko][ki]` case above.
                if _nu is None and isinstance(_ib, dict) and _ib.get("type") in ("Attribute", "FieldGet"):
                    _o = _ib.get("object"); _f = _ib.get("field") or _ib.get("attr")
                    if isinstance(_o, str):
                        _nu = self._self_field_dict_nu(f"{_o}.{_f}")
                if _nu and _nu.startswith("map "):
                    _inner_v = (_nu.split("(option ", 1)[1].rsplit(")", 1)[0]
                                if "(option " in _nu else "int")
                    _idef = '""' if _inner_v == "string" else "0"
                    # inner key κi: a `map string` inner passes the key through; an int-keyed inner
                    # (`map int …`, incl. nested-map.md's str-keys-hashed convention) hashes a STRING
                    # key with `str_hash_op`, else int-coerces.
                    _idx_ir = expr.get("index", {})
                    if "map string" in _nu:
                        _k = index
                    elif not self._in_spec and self._is_string_expr(_idx_ir):
                        self._add_abstract_op("val str_hash_op (s: string) : int")
                        _k = f"(str_hash_op {index})"
                    else:
                        _k = self._coerce_to_int(index)
                    # `value_str` (the inner `d[ko]` read) lowers to a program
                    # `begin assert..; match.. end` block carrying its OWN
                    # KeyError assert — it cannot sit inside the outer read's
                    # `assert { … }` logic formula. Hoist it into a `let` so the
                    # outer assert + `Map.get` reference a plain logic term.
                    _read = (f"(match Map.get _nmap {_k} "
                             f"with | Some v_ -> v_ | None -> {_idef} end)")
                    _wrapped = self._wrap_with_no_exception_assert(
                        ("map_get", None), ["_nmap", _k], _read)
                    return f"(let _nmap = {value_str} in {_wrapped})"
            var_name = value.get("name", "") if value.get("type") == "Var" else ""
            index_ir = expr.get("index", {})
            if (var_name and index_ir.get("type") == "Number" and
                    isinstance(index_ir.get("value"), (int, float))):
                idx_val = int(index_ir["value"])
                known_elems = getattr(self, "_known_collection_elements", {})
                if var_name in known_elems and idx_val in known_elems[var_name]:
                    return known_elems[var_name][idx_val]
            is_dict = var_name in getattr(self, "_dict_locals", set())
            is_array = not is_dict and (
                var_name in getattr(self, "_array2d_params", set()) or
                var_name in getattr(self, "_array_locals", set()) or
                var_name in getattr(self, "_inline_array_temps", set()) or
                var_name in getattr(self, "_current_array1d_params", set()))
            if not is_array and not is_dict and var_name:
                st = getattr(self, "_current_symbol_table", {})
                if st.get(var_name) == "list":
                    is_array = True
                elif st.get(var_name) in ("dict", "set", "frozenset"):
                    is_dict = True
            # `self.<field>[k]` where the field is set/dict/array-typed.
            if not is_array and not is_dict and value.get("type") in ("Attribute", "FieldGet"):
                ft = self._field_type_of(value)
                if ft in ("set", "dict", "frozenset"):
                    is_dict = True
                elif ft in ("list", "tuple", "bytes", "bytearray"):
                    is_array = True
            if is_array:
                # arity2.md (2b): parenthesise a ref-bound array deref (`!x`)
                # before subscripting, else `!x[i]` parses as `!(x[i])`.
                arr_e = f"({value_str})" if value_str.startswith("!") else value_str
                inner = f"{arr_e}[{index}]"
                # no_exception IndexError → assert in_bounds before the read.
                length_expr = f"(Array.length {arr_e})"
                return self._wrap_with_no_exception_assert(
                    ("subscript", "read"), [length_expr, index], inner)
            elif is_dict:
                # Body dict subscript read: `d[k]` →
                # `match Map.get !d k with Some v -> v | None -> 0 end`.
                # For body-local dicts, `value_str` already includes the
                # `!` deref because `_handle_var_expr` treats them as
                # refs. For `self.<dict-field>` accesses, no deref is
                # needed (record-field access is direct).
                dvar = value.get("name", "") if value.get("type") == "Var" else ""
                # no-more-int-3 A1 T1.2: a string KEY (κ) is passed through
                # unhashed (`map string …`); T1.1: a string VALUE reads back a
                # `string`, so the `None` arm is a typed placeholder (`""`) —
                # proven dead under `#@ no_exception KeyError` (faithful read),
                # the ambient default otherwise.
                if getattr(self, "_dict_key_types", {}).get(dvar) == "string":
                    k = index
                elif (not self._in_spec
                      and self._is_string_expr((expr.get("slice") or expr.get("index") or {}))):
                    # typed-ir-for-b-ceiling.md §9: a STRING key into an int-keyed body
                    # dict (`bitwise_ops = {"&": "bit_and", …}` → `map _ (option int)`) is
                    # `str_hash_op`-hashed — the SAME as the `in`-membership above, so both
                    # agree on the key type. Byte-identical (int key keeps `_coerce_to_int`).
                    self._add_abstract_op("val str_hash_op (s: string) : int")
                    k = f"(str_hash_op {index})"
                else:
                    k = self._coerce_to_int(index)
                # The missing-key placeholder is typed per ν (consolidated).
                default = self._dv_missing_default(
                    getattr(self, "_dict_value_types", {}).get(dvar))
                # list-comprehension-lowering.md L5: a self-field dict read
                # (`self._abstract_ops[k]`) has no `dvar`; its value type comes from the
                # record field → a `string` field defaults to "" (not the int `0`).
                if not dvar and value.get("type") in ("Attribute", "FieldGet"):
                    _o = value.get("object")
                    _f = value.get("field") or value.get("attr")
                    _fnu = (self._self_field_dict_nu(f"{_o}.{_f}")
                            if isinstance(_o, str) else None)
                    if _fnu == "string":
                        default = '""'
                    elif (isinstance(_fnu, str) and _fnu.startswith("map int (")
                          and _fnu.endswith(")")):
                        # nested-map.md: a NESTED-dict field read (`self._class_constants[k]`)
                        # yields the INNER map; the missing-key default is the empty inner map
                        # (`const None`), not the int `0`.
                        default = f"(const (None: {_fnu[len('map int ('):-1]}))"
                inner = f"(match Map.get {value_str} {k} with | Some v_ -> v_ | None -> {default} end)"
                # no_exception KeyError → assert has_key before the read.
                return self._wrap_with_no_exception_assert(
                    ("map_get", None), [value_str, k], inner)
            else:
                self._add_abstract_op("val subscript_get (x: int) (i: int) : int")
                return f"(subscript_get {self._coerce_to_int(value_str)} {self._coerce_to_int(index)})"
        else:
            return f"(Map.get !{self._heap_var} ({value_str} + {index}))"

    def _handle_attribute_expr(self, node: "ExprIR", local_refs: Set[str],
                               invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """Handle non-self attribute access: record field or abstract getter."""
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        obj_ir = expr.get("object", {})
        attr = expr.get("attr", "unknown")
        # 07-0903 W2: `\result.<field>` — field access on a record-returning function's
        # result. The WhyML result is the record value; emit `result.<field_label>`.
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Result":
            return f"result.{self._field_label(getattr(self, '_func_return_type', None), attr)}"
        # scc3.md Phase A: a quantifier-bound record var `o : C` (registered by
        # `_push_quant_binder`) — `o.field` is the record field, qualified via
        # `_field_label`, not an abstract `get_field` stub. (The class invariant is
        # already a Why3 type invariant on `c`, so the quantifier is sound.)
        if isinstance(obj_ir, dict) and obj_ir.get("type") == "Var":
            _vn = obj_ir.get("name", "")
            _qcls = self._quant_record_binders.get(_vn)
            if _qcls is not None:
                _cl = self._record_types[_qcls]["whyml_name"]
                return f"{whyml_ident(_vn)}.{self._field_label(_cl, attr)}"
            # inline.md Phase 1: a module-level global object `g : C` — `g.field` is the
            # global record's field (qualified via `_field_label`), not a `get_field` stub.
            _gcls = self._module_global_classes.get(_vn)
            if _gcls is not None and _gcls in self._record_types:
                _cl = self._record_types[_gcls]["whyml_name"]
                return f"{whyml_ident(_vn)}.{self._field_label(_cl, attr)}"
        if isinstance(obj_ir, str):
            return f"(get_{attr} {obj_ir})"
        if obj_ir.get("type") == "Var":
            var_name = obj_ir.get("name", "")
            if var_name in self._record_locals:
                # B1.4 (b1-plan.md §10): an AMBIGUOUS field (shared by >1 record —
                # e.g. `target`/`value` across the imported Stmt dataclasses) is
                # declared as the qualified label `<record>_<field>`, so its access
                # must qualify too, else Why3 reports the bare name unbound. Resolve
                # the record type from the symbol table and qualify via `_field_label`
                # using the record's own whyml_name (the key may be CamelCase or
                # lowered). Non-ambiguous fields keep the exact bare form —
                # byte-identical for every existing (local-record) driver.
                _rt = getattr(self, "_record_types", {})
                _ot = getattr(self, "_current_symbol_table", {}).get(var_name)
                if attr in getattr(self, "_ambiguous_fields", set()) and _ot:
                    _key = _ot if _ot in _rt else (_ot.lower() if _ot.lower() in _rt else None)
                    if _key is not None:
                        _rl = _rt[_key].get("whyml_name", _ot.lower())
                        return f"{whyml_ident(var_name)}.{self._field_label(_rl, attr)}"
                return f"{whyml_ident(var_name)}.{attr}"
        # self-ir-schema.md IR2: `<emit_ir>.value` / `.target` / … (a StmtIR field access on
        # an emit_ir node, e.g. `body_stmts[-1].value`) is an opaque emit_ir SUB-NODE —
        # `svalue_of` returns `IrOther ""` for a non-IrSub node (sound; content unmodeled),
        # so `… is not None` type-checks (always-present, §B-C4). @mutable_state-gated.
        if (self._is_emit_ir_expr(obj_ir)
                and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            _os = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
            # self-tcb-reduction T1.a: `<emit_ir>.kind` is the DISCRIMINANT (`kind_of`, a string),
            # not a sub-node — so `inner.kind == "Subscript"` routes through `str_eq_op`.
            if attr in _EMIT_IR_STR_ATTRS:
                return f"({_EMIT_IR_STR_ATTRS[attr]} {_os})"
            # self-tcb-reduction T1.a: a node-LIST attr (`node.elts`/`node.parts`/…) → the args
            # list (`args_of`, an `array emit_ir`), so `for elt in node.elts` iterates it.
            if attr in ("elts", "parts", "args", "captures"):
                return f"(args_of {_os})"
            return f"(svalue_of {_os})"
        obj_str = self._expr_to_whyml(obj_ir, local_refs, invariant_ctx, subst)
        self._add_abstract_op(f"val get_{attr} (x: int) : int")
        return f"(get_{attr} {obj_str})"

    def _var_todict_alias(self, name: str, local_refs: Set[str],
                          subst: Optional[Dict[str, str]]) -> str:
        """If `name` is a `to_dict()` ALIAS (`_todict_aliases[name] == "self.types"`), rebuild the
        dotted attribute IR and re-emit it; else return `""` (no alias — a dotted alias emission is
        never empty). Extracted (07-03-refactor R1) as the ONE hard branch of `_handle_var_expr` —
        it carries the `_parts = alias.split(".")` seq-slice for-loop whose `variant {}` references a
        program `val` in a logic context (the R7 target), isolating it so the rest of var proves."""
        _al = getattr(self, "_todict_aliases", {}).get(name)
        if _al is None:
            return ""
        _parts = _al.split(".")
        _n: Dict[str, Any] = {"type": "Var", "name": _parts[0]}
        for _p in _parts[1:]:
            _n = {"type": "Attribute", "object": _n, "attr": _p}
        return self._expr_to_whyml(_n, local_refs, False, subst)

    def _handle_var_expr(self, node: "ExprIR", local_refs: Set[str],
                         subst: Optional[Dict[str, str]] = None) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature
        name = expr["name"]
        if subst and name in subst:
            name = subst[name]
        # todict-reflection-plan.md R1 (var-substitution): `d = node.to_dict()` binds
        # `d` as a full ALIAS of the typed node — so a bare `d` reference (e.g. passing
        # `d` to `self._expr_to_whyml(d)`, the emitter's recursive sub-expression
        # emission) lowers to the node itself. Complements the `d.get(key)` routing:
        # both the reflective reads AND the recursive re-emission see the typed node.
        _alias = self._var_todict_alias(name, local_refs, subst)
        if _alias:
            return _alias
        # body-gate gap-5: a scalar quantifier binder reads BARE (a bound logic var),
        # shadowing a same-named loop/local ref for the quantifier body's duration.
        if name in getattr(self, "_quant_scalar_binders", ()):
            return whyml_ident(name)
        if name in self._array_locals:
            return whyml_ident(name)
        if name in self._lambda_locals:
            return whyml_ident(name)
        if name in self._record_locals:
            return whyml_ident(name)
        if name in local_refs:
            return f"!{whyml_ident(name)}"
        if name in self._current_params or name == "self":
            return whyml_ident(name) if name != "self" else name
        if name in self._shared_var_names:
            return f"!{whyml_ident(name)}"
        # module-constants-plan: a module-level int constant resolves to its literal,
        # in both body and contract (so e.g. `kinds[0] == K_IHDR` discharges). Comes
        # after the local/param/shared checks, so a same-named local correctly shadows
        # it. Replaces the opaque `val constant` for these names.
        if name in self._module_constants:
            _cv = self._module_constants[name]
            # 0442.md C5 (no-more-int): a string-literal constant folds to a real Why3
            # string literal, not an int hash; an int constant folds to its value.
            if isinstance(_cv, str):
                return self._whyml_string_literal(_cv)
            return f"({_cv})"
        # inline.md Phase 1: a bare reference to a module-level global object resolves to
        # its binding name (e.g. passing `acc` as an argument). After the local/param
        # checks so a same-named local shadows it.
        if name in getattr(self, "_module_global_classes", {}):
            return whyml_ident(name)
        # sum-types: a nullary `#@ datatype` constructor used as a value (`Red`).
        if name in self._constructors and self._constructors[name]["arity"] == 0:
            return name
        # 07-0647-spec S1.2: a bare class NAME used as a VALUE (e.g. the type argument
        # of `isinstance(x, C)`) must NOT reuse the record/variant TYPE name as its
        # opaque constant — `type c` and `val constant c` would collide (a kind/type
        # error). Give the value a distinct namespace.
        if name in self._record_types or name in getattr(self, "_variant_types", {}):
            csafe = f"_class_{whyml_ident(name)}"
            self._add_abstract_op(f"val constant {csafe} : int")
            return csafe
        safe = whyml_ident(name)
        self._add_abstract_op(f"val constant {safe} : int")
        return safe

    def _quant_binder_whyml(self, binder_type: str) -> str:
        """quantification.md: map a quantifier binder type to its WhyML sort.
        `None` ⇒ legacy `int` (emitted verbatim → byte-identical for every existing
        quantifier). Scalars map int→int / bool→bool / str→string / float→real; a
        declared `#@ datatype` or class name lowers to its Why3 type (lowercased,
        e.g. `Color`→`color`). Module 4 has already rejected an unresolved name."""
        if not binder_type:
            return "int"
        scalars = {"int": "int", "bool": "bool", "str": "string", "float": "real"}
        # 07-1311 Q4: collection-typed binders lower to their faithful WhyML sort.
        collections = {"list": "array int", "bytes": "array int",
                       "bytearray": "array int", "dict": "map int (option int)"}
        if binder_type in scalars:
            return scalars[binder_type]
        if binder_type in collections:
            return collections[binder_type]
        return whyml_ident(str(binder_type).lower())

    def _push_quant_binder(self, var: Optional[str], binder_type: Optional[str]):
        """scc3.md Phase A: register a quantifier-bound *record* var so `var.field`
        in the body lowers to the record field. No-op for scalar/datatype/None
        binders (only declared record classes have field access). Returns a restore
        token consumed by `_pop_quant_binder` (nesting/shadowing-safe)."""
        # 07-1311 Q4: a `dict`-typed binder is registered in `_dict_locals` (push/pop)
        # so `m[k]` in the body lowers to `Map.get m k`, not the abstract int subscript.
        if var and binder_type == "dict":
            dl = self._dict_locals
            had_d = var in dl
            dl.add(var)
            return ("dict", had_d)
        if not var or binder_type not in getattr(self, "_record_types", {}):
            # body-gate gap-5: register a scalar/None-typed binder so `_handle_var_expr`
            # reads it BARE (a logic var), shadowing any same-named `local_refs` member
            # (a loop var) for the duration of the quantifier body. No-op when var is None.
            if var:
                sb = self._quant_scalar_binders
                had_s = var in sb
                sb.add(var)
                return ("scalar", had_s)
            return ("noop", None)
        had = var in self._quant_record_binders
        prev = self._quant_record_binders.get(var)
        self._quant_record_binders[var] = binder_type
        return (had, prev)

    def _pop_quant_binder(self, var: Optional[str], token) -> None:
        kind, prev = token
        if kind == "noop":
            return
        if kind == "scalar":
            if not prev:            # was not already a scalar binder (nesting/shadowing)
                self._quant_scalar_binders.discard(var)
            return
        if kind == "dict":
            if not prev:                      # was not previously a dict local
                self._dict_locals.discard(var)
            return
        if kind:
            self._quant_record_binders[var] = prev
        else:
            self._quant_record_binders.pop(var, None)

    def _field_label(self, record_lower: str, field: str) -> str:
        """WhyML label for a record field. Ambiguous names (shared by >1
        record, e.g. an inherited field) are qualified `<record>_<field>` to
        avoid Why3's global field-label collision; unique names stay bare."""
        base = whyml_ident(field)
        if field in getattr(self, "_ambiguous_fields", set()) and record_lower:
            return f"{whyml_ident(record_lower)}_{base}"
        return base

    def _handle_field_get_expr(self, node: "ExprIR", invariant_ctx: bool) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature
        if invariant_ctx:
            return self._field_label(self._emit_record_ctx, expr['field'])
        obj = expr['object']
        field = expr['field']
        # Class-body integer constant referenced as `self.CONST` → its literal.
        self_type = self._current_self_type
        if (obj == "self" and self_type
                and field in self._class_constants.get(self_type, {})):
            return f"({self._class_constants[self_type][field]})"
        decl_fields = self._all_record_fields
        if field in decl_fields:
            return f"{obj}.{self._field_label(self_type, field)}"
        hash_field = stable_hash(field)
        self_type = self._current_self_type
        if obj == "self" and self_type:
            name = f"getattr_{self_type}"
            self._add_abstract_op(f"val {name} (x: {self_type}) (f: int) : int")
        else:
            name = "getattr_2"
            self._add_abstract_op(f"val {name} (x: int) (f: int) : int")
            obj = self._coerce_to_int(obj)
        return f"({name} {obj} {hash_field})"

    def _fstring_str_part(self, pp: "ExprIR", local_refs: Set[str],
                          invariant_ctx: bool, subst: Dict[str, str]) -> str:
        """One segment of a MIXED (str/int) f-string in a @mutable_state class: a string
        segment passes through; an int/opaque segment is `int_to_string`-wrapped. Hoisted
        (07-03-refactor R2) from the `_sp` nested closure in `_handle_fstring_expr` so the
        segment logic types identically under proof mode and `--no-proof`."""
        w = self._expr_to_whyml(pp, local_refs, invariant_ctx, subst)
        return w if self._is_string_expr(pp) else f"(int_to_string {self._coerce_to_int(w)})"

    def _handle_fstring_expr(self, node: "ExprIR", local_refs: Set[str],
                              invariant_ctx: bool, subst: Dict[str, str]) -> str:
        expr = node.to_dict()   # Phase-B-expr: typed signature; deep body stays dict-based
        parts = expr.get("parts", [])
        if not parts:
            return "0"
        # b14 B2: an f-string whose EVERY segment is string-typed (literal text and
        # `str`-typed interpolations) lowers to a faithful Why3 `string` concat chain
        # — the same `str_concat_op`/`concat` bridge as `s + t` (strings-plan Stage 2)
        # — instead of collapsing each segment to an int hash. A mixed f-string (any
        # int/opaque interpolation) keeps the legacy int-hash model below, so the
        # corpus that interpolates non-string values stays byte-identical.
        if all(self._is_string_expr(p) for p in parts):
            acc = self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst)
            # 07-03-refactor R2 (finish): a `for` over `parts[1:]` (array-emit_ir slice, R7) gets the
            # auto index-bound invariant so `parts[i]` discharges -- unlike the manual
            # `while i_part < n_parts` (bound in a local, no `Array.length` relation).
            for part in parts[1:]:
                p = self._expr_to_whyml(part, local_refs, invariant_ctx, subst)
                if self._in_spec:
                    acc = f"(concat {acc} {p})"
                else:
                    self._add_abstract_op(
                        "val str_concat_op (a: string) (b: string) : string\n"
                        "    ensures { result = (concat a b) }\n"
                        "    ensures { String.length result = String.length a + String.length b }")
                    acc = f"(str_concat_op {acc} {p})"
            return acc
        # todict-reflection-plan.md R3: in a @mutable_state class (the emitter model),
        # a MIXED str/int f-string (e.g. a gensym `f"__x_{n}"`) is still a STRING — the
        # int segments convert via `int_to_string`. So an emitter local bound to it types
        # as `string`. Gated on @mutable_state → byte-identical for every other f-string.
        if (not self._in_spec and getattr(self, "_current_self_type", None)
                in getattr(self, "_mutable_state_classes", set())):
            self._add_abstract_op("val int_to_string (n: int) : string")
            self._add_abstract_op(
                "val str_concat_op (a: string) (b: string) : string\n"
                "    ensures { result = (concat a b) }\n"
                "    ensures { String.length result = String.length a + String.length b }")

            acc = self._fstring_str_part(parts[0], local_refs, invariant_ctx, subst)
            for pp in parts[1:]:
                acc = f"(str_concat_op {acc} {self._fstring_str_part(pp, local_refs, invariant_ctx, subst)})"
            return acc
        acc = self._coerce_str_arg(self._expr_to_whyml(parts[0], local_refs, invariant_ctx, subst))
        for part in parts[1:]:
            p = self._coerce_str_arg(self._expr_to_whyml(part, local_refs, invariant_ctx, subst))
            self._add_abstract_op("val str_concat (x: int) (y: int) : int")
            acc = f"(str_concat {acc} {p})"
        return acc

    def _handle_unaryop_expr(
        self,
        node: "UnaryOpExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is a UnaryOpExpr (op: str, expr: ExprIR).
        e = self._expr_to_whyml(node.expr, local_refs, invariant_ctx, subst)
        op = op_translate(node.op)
        if op == "+":
            return e
        if op == "~":
            # 0442.md C4: Python bitwise NOT on the int model is the two's-complement
            # identity `~x == -x - 1` (genuine int op, not a type-class leak).
            return f"((- {e}) - 1)"
        if op == "not":
            e = self._to_bool(e, node.expr.to_dict())
        return f"({op} {e})"

    def _handle_old_expr(
        self,
        node: "OldExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is an OldExpr (expr: ExprIR).
        inner = node.expr
        if not self._value_semantic and inner.kind == "Subscript":
            d = inner.to_dict()
            value = self._expr_to_whyml(d["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(d["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get (old !{self._heap_var}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"(old {e})"

    def _handle_at_expr(
        self,
        node: "AtExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. `node` is an AtExpr (expr: ExprIR, label: str).
        label = node.label
        inner = node.expr
        if label == "PRE":
            e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
            return f"(old {e})"
        if inner.kind == "Subscript" and not self._value_semantic:
            d = inner.to_dict()
            value = self._expr_to_whyml(d["value"], local_refs, invariant_ctx, subst)
            index = self._expr_to_whyml(d["index"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({self._heap_var} at {label}) ({value} + {index}))"
        e = self._expr_to_whyml(inner, local_refs, invariant_ctx, subst)
        return f"({e} at {label})"

    def _cf5_arr(self, d: "ExprIR") -> bool:
        """True if an IfExp arm `d` is a STRING-seq value (`.split(...)`, a list/comp literal,
        or a str-seq/str-array Var) — so a `<seq> if c else <seq>` IfExp emits each arm seq-ified
        rather than int-coerced. Hoisted (07-03-refactor R2) from the nested closure in
        `_handle_ifexpr_expr` so the arm predicate types consistently under proof mode."""
        if not isinstance(d, dict):
            return False
        _tt = d.get("type")
        if (_tt == "Call" and isinstance(d.get("func"), str)
                and d["func"].endswith(".split")):
            return True
        if _tt in ("ArrayLit", "ListLit", "ListComp"):
            return True
        if _tt == "Var":
            return (getattr(self, "_seq_value_types", {}).get(d.get("name")) == "string"
                    or getattr(self, "_array_elem_types", {}).get(d.get("name")) == "string")
        return False

    #@ requires_method _seq_operand: (self, val_ir: ExprIR, local_refs: set) -> str
    def _ifexpr_seq_arm(self, test: str, _bd: "ExprIR", _od: "ExprIR",
                        local_refs: Set[str]) -> str:
        """CF5: a ternary whose BOTH arms are `seq string` name-lists (`exc.split("|") if … else
        [exc]`) — emit each arm seq-ified (`_seq_operand`). Extracted (07-03-refactor R2/R1-pattern)
        as the ONE branch of `_handle_ifexpr_expr` that stays trusted (its `_seq_operand` result +
        `local_refs or set()` map-or don't yet lower cleanly), isolating it so the rest converts."""
        # 07-03-refactor: `_ifexpr_seq_arm` is only reached from the @mutable_state seq-arm where
        # `local_refs` is always a present Set, so `or set()` is a no-op (avoids the map-or lowering).
        return (f"(if {test} then {self._seq_operand(_bd, local_refs)} "
                f"else {self._seq_operand(_od, local_refs)})")

    def _handle_ifexpr_expr(
        self,
        node: "IfExprExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. IfExprExpr (test, body, orelse: ExprIR).
        test = self._expr_to_whyml(node.test, local_refs, invariant_ctx, subst)
        test = self._to_bool(test, node.test.to_dict())
        # 07-03-refactor R2: split the tuple-unpack into two assignments so each arm types as
        # emit_ir (via the `.to_dict()` recognizer) instead of the int tuple-unpack target.
        _bd = node.body.to_dict()
        _od = node.orelse.to_dict()
        body = self._expr_to_whyml(node.body, local_refs, invariant_ctx, subst)
        orelse = self._expr_to_whyml(node.orelse, local_refs, invariant_ctx, subst)
        # i-feel-good.md I-A/I-B: a ternary is a STRING expression when at least one arm is
        # string-typed and the other is string-or-`None` — emit the string arms directly (a
        # bare `""`/`"lit"` stays a WhyML string, a `None` arm → "" the absent sentinel), so
        # `arr.get("name","") if … else ""` and `d.get(k) if k else None` type-check as
        # string. @mutable_state-gated → the corpus int model is byte-identical.
        _ms = (getattr(self, "_current_self_type", None)
               in getattr(self, "_mutable_state_classes", set()))
        _b_str = self._is_string_expr(_bd)
        _o_str = self._is_string_expr(_od)
        _b_none = _bd.get("type") == "None"
        _o_none = _od.get("type") == "None"
        if _ms and (_b_str or _o_str) and (_b_str or _b_none) and (_o_str or _o_none):
            if _b_none: body = '""'
            if _o_none: orelse = '""'
            return f"(if {test} then {body} else {orelse})"
        # item34.md CF1: the emit_ir analogue — `stmt.value.to_dict() if stmt.value is not
        # None else None` (an `Optional[ExprIR]` ternary) is an emit_ir expression; a `None`
        # arm → `(IrOther "")` (the emit_ir absent sentinel). @mutable_state.
        _b_ir = self._is_emit_ir_expr(_bd)
        _o_ir = self._is_emit_ir_expr(_od)
        if _ms and (_b_ir or _o_ir) and (_b_ir or _b_none) and (_o_ir or _o_none):
            if _b_none: body = '(IrOther "")'
            if _o_none: orelse = '(IrOther "")'
            return f"(if {test} then {body} else {orelse})"
        # item34.md CF5: a ternary whose BOTH arms are `seq string` name-lists (`exc.split("|")
        # if "|" in exc else [exc]`) — emit each arm seq-ified (`_seq_operand`), no int
        # coercion. @mutable_state.
        if _ms and self._cf5_arr(_bd) and self._cf5_arr(_od):
            return self._ifexpr_seq_arm(test, _bd, _od, local_refs)
        body = self._coerce_to_int(body)
        orelse = self._coerce_to_int(orelse)
        return f"(if {test} then {body} else {orelse})"

    def _handle_named_expr_expr(
        self,
        node: "NamedExprExpr",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        # Phase-B-expr: typed. NamedExprExpr (target: str, value: ExprIR).
        target = whyml_ident(node.target)
        v = self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        if target in local_refs:
            return f"(begin {target} := {v}; !{target} end)"
        local_refs.add(target)
        return f"(let {target} = ref {v} in !{target})"

    #@ requires_method _field_type_of: (self, attr_ir: ExprIR) -> str
    def _slice_array_or_opaque(self, node: "ExprIR", arr: str, sl: "ExprIR",
                               local_refs: Set[str], invariant_ctx: bool,
                               subst: Optional[Dict[str, str]]) -> str:
        """The array-source / opaque tail of `_handle_slice_access_expr`: `Array.sub` for a known
        array source (`_field_type_of(val) in list/tuple/…`), else the opaque `array_slice`.
        Extracted (07-03-refactor R4) as the trusted leaf — it calls `_field_type_of` (types.py),
        whose cross-file stub defaults to int, so the whole tail stays trusted while the seq/string
        slice cases in `_handle_slice_access_expr` convert."""
        lo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
        hi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst) if sl.get("upper") else f"(Array.length {arr})"
        val = node.value.to_dict()
        is_array_src = False
        if val.get("type") in ("Attribute", "FieldGet"):
            if self._field_type_of(val) in ("list", "tuple", "bytes", "bytearray"):
                is_array_src = True
        elif val.get("type") == "Var":
            vn = val.get("name", "")
            if (vn in getattr(self, "_array_locals", set()) or
                    vn in getattr(self, "_current_array1d_params", set()) or
                    self._current_symbol_table.get(vn) == "list"
                    or vn in getattr(self, "_array_elem_types", {})):
                is_array_src = True
        if is_array_src:
            return f"(Array.sub {arr} ({lo}) (({hi}) - ({lo})))"
        self._add_abstract_op("val array_slice (a: array int) (lo: int) (hi: int) : array int")
        # 07-03-refactor: store the coerced arg in a fresh local (not a reassigned param) so `arr`
        # stays an immutable string param — else the `{arr}` interpolations lower to `!arr` (ref).
        _carr = self._array_coerce_arg(arr)
        return f"(array_slice {_carr} {lo} {hi})"

    def _handle_slice_access_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        arr = self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        sl = node.slice.to_dict()
        # seq-model-pivot.md SQ3: a slice of a seq local (`body_stmts[:-1]`) is a seq
        # sub-sequence (`seq_sub`) — a pure immutable value, NO `array_slice`/region. Content
        # opaque; the length law is conditional (sound). @mutable_state (via _seq_locals).
        _bv = node.value.to_dict()
        if (_bv.get("type") == "Var" and _bv.get("name") in getattr(self, "_seq_locals", set())):
            _slo = (self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst)
                    if sl.get("lower") else "0")
            _shi = (self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst)
                    if sl.get("upper") else f"(Seq.length {arr})")
            self._add_abstract_op(
                "val seq_sub (s: seq 'a) (lo hi: int) : seq 'a\n"
                "    ensures { 0 <= lo <= hi <= Seq.length s -> Seq.length result = hi - lo }")
            return f"(seq_sub {arr} {_slo} {_shi})"
        # strings-plan Stage 2: `s[a:b]` on a string is `String.substring s a (b-a)`. Spec
        # uses the logic symbol; body bridges through `str_sub_op` (and `str_length_op` for an
        # omitted upper bound), since `String.substring`/`String.length` aren't program values.
        if self._is_string_expr(node.value.to_dict()):
            slo = self._expr_to_whyml(sl["lower"], local_refs, invariant_ctx, subst) if sl.get("lower") else "0"
            if sl.get("upper"):
                shi = self._expr_to_whyml(sl["upper"], local_refs, invariant_ctx, subst)
            elif self._in_spec:
                shi = f"(String.length {arr})"
            else:
                self._add_abstract_op("val str_length_op (s: string) : int\n"
                                      "    ensures { result = (String.length s) }")
                shi = f"(str_length_op {arr})"
            slen = f"(({shi}) - ({slo}))"
            if self._in_spec:
                return f"(String.substring {arr} {slo} {slen})"
            # The length lemma is baked into the bridge's `ensures`: deriving
            # `String.length (substring s lo len) = len` from the substring theory makes the
            # SMT backend OOM for general (non-literal) args, but the fact is sound (cf. the
            # Stage-0 literal probe), so we supply it directly under its bounds guard.
            self._add_abstract_op(
                "val str_sub_op (s: string) (lo len: int) : string\n"
                "    ensures { result = (String.substring s lo len) }\n"
                "    ensures { (0 <= lo /\\ 0 <= len /\\ lo + len <= String.length s)"
                " -> String.length result = len }")
            return f"(str_sub_op {arr} {slo} {slen})"
        return self._slice_array_or_opaque(node, arr, sl, local_refs, invariant_ctx, subst)

    def _handle_arraylen_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
            var = node.var
            # 07-1705-rev4 P3/P5: `\length(a)` of a seq-modelled list — BODY context only.
            # In a pre/post-condition a seq-promoted *param* names the original `array int`
            # entry value (the body seq shadow is out of scope), so fall through to
            # `Array.length` there.
            if var in getattr(self, "_seq_locals", set()) and not self._in_spec:
                deref = "!" if var in local_refs else ""
                return f"(Seq.length {deref}{whyml_ident(var)})"
            if var == "\\result":
                return f"(Array.length {getattr(self, '_result_alias', None) or 'result'})"
            if var.startswith("self."):
                field = var[len("self."):]
                # Mirror `_handle_field_get_expr`: in a type/class invariant
                # the record fields are bare; in a method contract `self`
                # is an in-scope parameter.
                ref = field if invariant_ctx else f"self.{field}"
                return f"(Array.length {ref})"
            # An array LOCAL (`out = [0]*n`) is bound as a plain `Array.make` mutable
            # array, NOT a ref — so it is referenced BARE even when it also appears in
            # `local_refs` (mirrors `_handle_var_expr`'s `_array_locals` rule). Without
            # this guard `\length(out)` in a loop invariant emitted `Array.length !out`,
            # a deref of a non-ref → typecheck failure (`len(out)` and subscript `out[i]`
            # were already correct via `_handle_var_expr`; only this `\length` path wasn't).
            deref = ("!" if (var in local_refs
                             and var not in getattr(self, "_array_locals", set()))
                     else "")
            return f"(Array.length {deref}{var})"
        return f"{node.var}_len"

    def _module_binding_names(self) -> Set[str]:
        """07-1839 P2: statically-declared module-level names — the sound lower bound for
        `\\in_globals` (functions, module-global object instances, module constants, and
        classes). The world is OPEN beyond this (import/exec), so a name's absence here is
        *unknown*, never decided-false."""
        ir = getattr(self, "ir", {})
        names: Set[str] = {f.get("name") for f in ir.get("functions", [])}
        names |= set(getattr(self, "_module_global_classes", {}))
        names |= set(getattr(self, "_module_constants", {}))
        names |= {c.get("name") for c in ir.get("classes", []) if isinstance(c, dict)}
        names.discard(None)
        return names

    def _handle_in_globals_expr(self, node: "ExprIR", local_refs: Set[str],
                                invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P2: `\\in_globals(name)` — three-valued, true-only lower bound.
        decided-true (→ `true`) for a declared module binding; UNKNOWN otherwise → an
        uninterpreted bool (`in_globals_op`), so it is neither provably true nor false
        (open world: import/exec may inject the name). The unsound decided-false direction
        is never emitted."""
        name = node.name
        if name in self._module_binding_names():
            return "true"
        self._add_abstract_op("val function in_globals_op (n: int) : bool")
        return f"(in_globals_op {sum(ord(c) for c in name)})"

    def _handle_in_scope_expr(self, node: "ExprIR", local_refs: Set[str],
                              invariant_ctx: bool, subst: Optional[Dict[str, str]]) -> str:
        """07-1839 P3: `\\in_scope(name)` — three-valued via definite-assignment.
        decided-true (→ `true`) if `name` is assigned on all paths (param or top-level
        assignment before any branch/return); decided-false (→ `false`) if `name` is
        neither a param nor assigned anywhere; UNKNOWN (conditionally assigned) → an
        uninterpreted bool. A dynamic exec havocs the binding set, so the decided-false
        direction is withheld afterwards (decision C)."""
        name = node.name
        if name in getattr(self, "_scope_must", set()):
            return "true"
        if (not getattr(self, "_scope_dyn_exec", False)
                and name not in getattr(self, "_scope_all", set())
                and name not in getattr(self, "_scope_params", set())):
            return "false"
        self._add_abstract_op("val function in_scope_op (n: int) : bool")
        return f"(in_scope_op {sum(ord(c) for c in name)})"

    def _handle_valid_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        length = self._expr_to_whyml(node.length, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"({length} >= 0 && {length} <= Array.length {base})"
        return f"(valid !{self._heap_var} {base} {length})"

    def _handle_separated_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        if self._value_semantic:
            return "true"
        b1 = node.base1
        l1 = self._expr_to_whyml(node.len1, local_refs, invariant_ctx, subst)
        b2 = node.base2
        l2 = self._expr_to_whyml(node.len2, local_refs, invariant_ctx, subst)
        return f"(separated {b1} {l1} {b2} {l2})"

    def _handle_length2d_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        rows = self._expr_to_whyml(node.rows, local_refs, invariant_ctx, subst)
        cols = self._expr_to_whyml(node.cols, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"({base}.rows = {rows} && {base}.columns = {cols})"
        return "true"

    def _handle_valid2d_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        row = self._expr_to_whyml(node.row, local_refs, invariant_ctx, subst)
        col = self._expr_to_whyml(node.col, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(valid_index {base} {row} {col})"
        return "true"

    # ---- cleared-array.md S1–S4: content-faithful comprehensions ----------
    def _comp_elt_pure_int(self, elt: Any, free: Set[str]) -> bool:
        """True iff `elt` is a PURE, total `int`-valued expression built only
        from variables (collected into `free`), integer literals, and the total
        arithmetic operators `+ - *` (identity / arithmetic shapes). Division /
        modulo are excluded (partiality — ZeroDivisionError semantics must not
        leak into a logic `ensures`); calls / subscripts / attributes /
        comparisons / booleans are excluded (not guaranteed pure-int logic
        terms). Conservative: any unrecognised node ⇒ not liftable."""
        if not isinstance(elt, dict):
            return False
        t = elt.get("type")
        if t == "Var":
            free.add(elt.get("name", ""))
            return True
        if t == "Number":
            return isinstance(elt.get("value"), int)
        if t == "BinOp":
            if elt.get("op") not in ("+", "-", "*"):
                return False
            return (self._comp_elt_pure_int(elt.get("left", {}), free)
                    and self._comp_elt_pure_int(elt.get("right", {}), free))
        if t == "UnaryOp":
            if elt.get("op") not in ("-", "+"):
                return False
            return self._comp_elt_pure_int(elt.get("operand", elt.get("value", {})), free)
        return False

    def _content_comp(self, node: "ExprIR", local_refs: Set[str],
                      invariant_ctx: bool,
                      subst: Optional[Dict[str, str]]) -> Optional[str]:
        """cleared-array.md S1–S4. Emit a CONTENT-faithful comprehension for a
        supported element shape, or return None to fall through to the opaque
        length-only path. Supported: ONE generator whose target is a plain name,
        an `array int` source (NOT a seq local — the seq comprehension path owns
        those), and an element that is pure-int over the target ONLY (identity or
        `+ - *` arithmetic). A filter (`if`) keeps ONLY the sound length bound."""
        _d = node.to_dict()
        gens = _d.get("generators", []) or []
        if len(gens) != 1:
            return None
        g = gens[0]
        target = g.get("target")
        if not isinstance(target, str):
            return None
        src_ir = g.get("iter", {})
        # The seq comprehension path (mutable-state, `_seq_locals`) is left
        # untouched — its result must stay a reassignable `seq` value.
        if (isinstance(src_ir, dict) and src_ir.get("type") == "Var"
                and src_ir.get("name") in getattr(self, "_seq_locals", set())):
            return None
        elt = _d.get("elt", {})
        free: Set[str] = set()
        if not self._comp_elt_pure_int(elt, free):
            return None
        # The element may reference the loop target ONLY (no captured locals —
        # they are not parameters of the abstract `val`).
        if free - {target}:
            return None
        srcw = self._expr_to_whyml(src_ir, local_refs or set(), invariant_ctx, subst)
        srca = self._array_coerce_arg(srcw)
        n = getattr(self, "_comp_content_counter", 0)
        self._comp_content_counter = n + 1
        op = f"list_content_comp_{n}"
        has_if = bool(g.get("ifs"))
        if has_if:
            # cleared-array.md S4: a filtered comprehension keeps only the SOUND
            # length bound — the surviving elements are NOT at their source
            # indices, so no per-index content law holds.
            self._add_abstract_op(
                f"val {op} (src: array int) : array int\n"
                f"    ensures {{ Array.length result <= Array.length src }}")
            return f"({op} {srca})"
        # Lower the element with the loop target rebound to the per-index source
        # read `src[i]` (via a fresh scalar binder `_celt = src[i]`), in logic
        # context. The result is a pure int term over `_celt`.
        binder = "_ci"
        celt = "_celt"
        new_subst = dict(subst or {})
        new_subst[target] = celt
        sb = self._quant_scalar_binders
        had_celt = celt in sb
        sb.add(celt)
        saved_in_spec = self._in_spec
        self._in_spec = True
        try:
            eltw = self._expr_to_whyml(elt, local_refs or set(), True, new_subst)
        finally:
            self._in_spec = saved_in_spec
            if not had_celt:
                sb.discard(celt)
        self._add_abstract_op(
            f"val {op} (src: array int) : array int\n"
            f"    ensures {{ Array.length result = Array.length src }}\n"
            f"    ensures {{ forall {binder} : int. 0 <= {binder} < Array.length src ->\n"
            f"                result[{binder}] = (let {celt} = src[{binder}] in {eltw}) }}")
        return f"({op} {srca})"

    def _handle_issorted_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        lo = self._expr_to_whyml(node.lo, local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(node.hi, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(forall _si : int. {lo} <= _si /\\ _si < {hi} - 1 -> {base}[_si] <= {base}[_si + 1])"
        return "true"

    def _handle_arrayeq_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        """`\\array_eq(a, b)` — extensional array content equality:
        same length and equal element at every index. Emitted as an
        explicit quantified formula (rather than the `array_eq`
        predicate) so the SMT solver sees the per-index goal directly and
        can E-match it against `Array.blit`/`Array.sub` content
        postconditions (the predicate layer did not auto-unfold)."""
        a = self._expr_to_whyml(node.left, local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(node.right, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return (f"((Array.length {a} = Array.length {b}) /\\ "
                    f"(forall _ae : int. 0 <= _ae /\\ _ae < Array.length {a} "
                    f"-> {a}[_ae] = {b}[_ae]))")
        return "true"

    def _handle_permutation_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        """`\\permutation(a, b)` — `a` is a permutation of `b` (same multiset).
        Lowers to an UNINTERPRETED `predicate permut` (no-more-int A2b Gap 1):
        unlike `\\array_eq`, permutation is not first-order expressible, so it is
        NOT unfolded — a proof-assistant-imported axiom (`#@ proof`, stage 4) is
        what constrains `permut`. Here the operator is just plumbed: a spec-only
        relation over two `array int` values."""
        a = self._expr_to_whyml(node.left, local_refs, invariant_ctx, subst)
        b = self._expr_to_whyml(node.right, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            self._add_abstract_op("predicate permut (a: array int) (b: array int)")
            return f"(permut {a} {b})"
        return "true"

    def _handle_sum_node_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        base = node.base
        lo = self._expr_to_whyml(node.lo, local_refs, invariant_ctx, subst)
        hi = self._expr_to_whyml(node.hi, local_refs, invariant_ctx, subst)
        if self._value_semantic:
            return f"(pycsl_sum {base} {lo} {hi})"
        return "0"

    def _handle_lambda_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        params = node.params
        body = self._expr_to_whyml(node.body, local_refs, invariant_ctx, subst)
        param_str = " ".join(f"({whyml_ident(p)}: int)" for p in params) if params else "()"
        return f"(fun {param_str} -> {body})"

    def _handle_setlit_expr(
        self,
        node: "ExprIR",
        local_refs: Set[str],
        invariant_ctx: bool,
        subst: Optional[Dict[str, str]],
    ) -> str:
        elts = node.elts
        # Empty set literal: `map int (option int)` initialised to None.
        if not elts:
            return "(const (None: option int))"
        # Non-empty set literal `{a, b, c}`: chain map_update_some on an
        # empty base. Each element is marked present with value 0.
        # `Map.set` directly would be a logic-function call rejected as
        # ghost; the program-val wrapper sidesteps that.
        # list-comprehension-lowering.md L5: polymorphic decl in a @mutable_state module
        # (unifies with a string-valued dict field); fixed in the corpus → byte-identical.
        _poly = getattr(self, "_mutable_state_classes", None)
        self._add_abstract_op(
            ("val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
             ": map 'k (option 'v)\n" if _poly else
             "val map_update_some (m: map int (option int)) (k: int) (v: int) "
             ": map int (option int)\n")
            + "    ensures { result = Map.set m k (Some v) }")
        result = "(const (None: option int))"
        for elt in elts:
            elt_w = self._coerce_to_int(self._expr_to_whyml(
                elt, local_refs, invariant_ctx, subst))
            result = f"(map_update_some {result} {elt_w} 0)"
        return result

    def _expr_to_whyml(self, expr: "Union[Dict[str, Any], ExprIR]", local_refs: Set[str],
                       invariant_ctx: bool = False,
                       subst: Optional[Dict[str, str]] = None) -> str:
        """Recursively translates an expression dictionary into a WhyML string.
        When invariant_ctx is True, FieldGet emits bare field names (for record invariants).
        subst: optional name substitution dict applied before local_refs lookup (e.g. for-loop vars)."""
        # Phase-B-expr: accept a typed ExprIR (Phase-A sum) or the legacy wire
        # dict. Normalize to a typed node once; converted kinds dispatch by
        # isinstance below; un-converted kinds fall through to the legacy dict
        # body (`node.to_dict()`). Byte-identical at every kind conversion.
        if not expr: return ""
        node = expr_from_dict(expr) if isinstance(expr, dict) else expr
        # --- typed fast-paths (E2: leaf kinds) ---
        if isinstance(node, NumberExpr):
            v = node.value
            if isinstance(v, float) and not float(v).is_integer():
                return repr(v)
            if isinstance(v, float):
                return f"{int(v)}.0"
            return str(int(v))
        if isinstance(node, RawWhymlExpr):
            return node.whyml
        if isinstance(node, StringExpr):
            return whyml_string_literal(node.value)
        if isinstance(node, ResultExpr):
            return getattr(self, "_result_alias", None) or "result"
        if isinstance(node, NoneExpr):
            return "0"
        if isinstance(node, BoolExpr):
            if self._in_spec: return "true" if node.value else "false"
            return "1" if node.value else "0"
        if isinstance(node, UnknownPyExprExpr):
            return "0"
        if isinstance(node, SliceExpr):
            return "0"
        if isinstance(node, OldFieldExpr):
            _of_rec = (self._current_self_type if node.object == "self"
                       else (getattr(self, "_current_record_var_classes", {}).get(node.object, "") or "").lower() or None)
            return f"(old {node.object}.{self._field_label(_of_rec, node.field)})"
        if isinstance(node, StarredExpr):
            return self._expr_to_whyml(node.value, local_refs, invariant_ctx, subst)
        if isinstance(node, TupleExpr):
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in node.elts]
            return f"({', '.join(elts)})"
        # --- legacy dict body (un-converted kinds) ---
        expr = node.to_dict()
        t = expr["type"]

        # Simple literals and trivial 1-3-line branches — kept inline
        if t == "Number":
            v = expr["value"]
            # no-more-int Stage D: a float literal is a Why3 `real` constant (was
            # truncated to int — the unsound float collapse). Why3 reals need a decimal
            # point: `1.5`, `2.0`.
            if isinstance(v, float) and not float(v).is_integer():
                return repr(v)
            if isinstance(v, float):
                return f"{int(v)}.0"
            return str(int(v))
        # Pre-lowered WhyML passthrough — used to splice an already-emitted argument
        # string into a value IR (parametrized record construction, base_op.md Tier A).
        if t == "RawWhyml": return expr["whyml"]
        if t == "String":
            # strings-plan Stage 1: a string literal is a real Why3 string. Where an int is
            # required (an abstract-op arg, a dict key), `_coerce_to_int` hashes it back, so
            # int-contexts keep working; string-typed contexts now get a real `"..."`.
            # `whyml_string_literal` escapes raw newlines/tabs/control bytes (Why3 rejects
            # them with "illegal character in string") — `";\n"` lowers to `";\\n"`.
            return whyml_string_literal(expr["value"])
        if t == "Result":   return getattr(self, "_result_alias", None) or "result"
        if t == "None":     return "0"
        if isinstance(node, ArrayLitExpr):
            elts = expr.get("elts", [])
            # 07-0903 W1 (no-more-int): a list/array of tuples lowers to a faithful
            # `array (t0, …)` — each element is a Why3 tuple, NOT collapsed to an int.
            # Homogeneous fixed-arity tuples only (the directory/(key,value) shape);
            # a mixed-arity literal is still rejected (no single element type).
            tuple_elts = [e for e in elts if isinstance(e, dict) and e.get("type") == "Tuple"]
            if tuple_elts:
                arities = {len(e.get("elts", [])) for e in tuple_elts}
                if len(tuple_elts) != len(elts) or len(arities) != 1:
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        "array/list with mixed or non-tuple elements alongside tuples is "
                        "not supported: a faithful `array (tuple)` needs one uniform "
                        "element type. Use a uniform list of equal-arity tuples.")
                n = len(elts)
                # Each element is a Why3 tuple value `(a, b, …)` — no int coercion.
                lowered = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst)
                           for e in elts]
                inner = f"let _alit = Array.make {n} ({lowered[0]}) in"
                sets = "; ".join(f"_alit[{i}] <- {lowered[i]}" for i in range(1, n))
                if sets:
                    inner += f" {sets};"
                return f"({inner} _alit)"
            if elts:
                # Build a concrete `array int` of the literal's elements:
                # `(let _alit = Array.make N e0 in _alit[1] <- e1; …; _alit)`.
                n = len(elts)
                e0 = self._coerce_to_int(
                    self._expr_to_whyml(elts[0], local_refs, invariant_ctx, subst))
                sets = "; ".join(
                    f"_alit[{i}] <- {self._coerce_to_int(self._expr_to_whyml(e, local_refs, invariant_ctx, subst))}"
                    for i, e in enumerate(elts) if i > 0)
                inner = f"let _alit = Array.make {n} ({e0}) in"
                if sets:
                    inner += f" {sets};"
                return f"({inner} _alit)"
            return "(Array.make 1024 0)"
        if t == "UnknownPyExpr": return "0"
        if t == "Slice":    return "0"
        if t == "OldField":
            _of_rec = (self._current_self_type if expr['object'] == "self"
                       else (getattr(self, "_current_record_var_classes", {}).get(expr['object'], "") or "").lower() or None)
            return f"(old {expr['object']}.{self._field_label(_of_rec, expr['field'])})"
        if t == "Starred":  return self._expr_to_whyml(expr.get("value", {}), local_refs, invariant_ctx, subst)
        if t == "Bool":
            if self._in_spec: return "true" if expr.get("value") else "false"
            return "1" if expr.get("value") else "0"
        if t == "Tuple":
            elts = [self._expr_to_whyml(e, local_refs, invariant_ctx, subst) for e in expr.get("elts", [])]
            return f"({', '.join(elts)})"
        if isinstance(node, ForallExpr):
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            # M4: when lowering an opt-in `#@ propagate_frame` quantified frame
            # (`_frame_trigger_active`), pin a SPECIFIC trigger on the post-state term X of
            # `X == \old(X)` — but ONLY when X is a function APPLICATION (a decode like
            # `slot_inode self.disk x0 k`), whose trigger fires on `slot_inode` terms alone,
            # not on raw `self.disk[i]` bounds reads. Bare the term (Why3 mis-parses `[(t)]`).
            trig = ""
            if getattr(self, "_frame_trigger_active", False):
                tt = self._frame_trigger_term(expr['body'])
                if isinstance(tt, dict) and tt.get("type") == "Call":
                    _tl = self._expr_to_whyml(tt, local_refs, invariant_ctx, subst)
                    trig = f" [{self._strip_outer_parens(_tl)}]"
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(forall {node.var} : {bty}{trig}. {body})"
        if isinstance(node, ExistsExpr):
            bty = self._quant_binder_whyml(expr.get("binder_type"))
            saved = self._push_quant_binder(expr.get("var"), expr.get("binder_type"))
            body = self._expr_to_whyml(expr['body'], local_refs, invariant_ctx, subst)
            self._pop_quant_binder(expr.get("var"), saved)
            return f"(exists {node.var} : {bty}. {body})"
        if isinstance(node, ForallItemsExpr):
            # 07-1311 Q3: `\forall k, v in d.items(); P` → over the map+option model,
            # `forall k. match Map.get d k with Some v -> P | None -> true end`. The value
            # `v` is bound by the match; the key `k` (int) by the outer forall. Register
            # the map binder so a nested `d2[k]` in the body still lowers correctly.
            key, val = expr["key"], expr["val"]
            body = self._expr_to_whyml(expr["body"], local_refs, invariant_ctx, subst)
            return (f"(forall {key} : int. match Map.get ({expr['map']}) ({key}) with "
                    f"| Some {val} -> {body} | None -> true end)")
        if isinstance(node, MapValueIsExpr):
            # 07-1311 Q3: `\exists k. d[k] = Some v` — the value-membership witness for
            # `\forall v in d.values(); …`. A pure logic term over the `map`+`option` model.
            key = self._expr_to_whyml(expr["key"], local_refs, invariant_ctx, subst)
            val = self._expr_to_whyml(expr["value"], local_refs, invariant_ctx, subst)
            return f"(Map.get ({expr['map']}) ({key}) = Some ({val}))"
        if isinstance(node, DictLitExpr):
            # typing-engagement ty2 / 29-1700-typing-spec-5 §2.2 T8: a dict
            # literal `{"x": 1, "y": 2}` in a TypedDict construction context
            # (the enclosing function/assignment target is a TypedDict record)
            # lowers to a record literal `{ x = 1; y = 2 }`. The static plane
            # is Interpreted (record-literal type-checking); the runtime plane
            # is the plain-dict alias (Shimmed) — no blend. Non-TypedDict dict
            # literals fall through to the existing empty-map stub (byte-
            # identical).
            td_lit = self._typeddict_record_literal(expr, local_refs,
                                                    invariant_ctx, subst)
            if td_lit is not None:
                return td_lit
            # typed-ir-for-b-ceiling.md B-C1: an inline IR-node construction
            # `{"type": "Var", "name": e}` lowers to the typed `exprir` constructor
            # `(EVar <e>)`, not a heterogeneous map — so it unifies with a real ExprIR
            # field at a sibling that takes both. Gated on @mutable_state (the emitter
            # model); byte-identical for every other dict literal.
            irnode = self._lower_irnode_construction(expr, local_refs, invariant_ctx, subst)
            if irnode is not None:
                return irnode
            # Body dict literal: empty `map int (option int)`. Non-empty
            # dict literals would need element-by-element `Map.set` but
            # are currently uncommon enough to fall through to empty.
            # TODO: handle `{k1: v1, k2: v2}` by chaining Map.set.
            return "(const (None: option int))"
        if isinstance(node, ListCompExpr):
            # cleared-array.md S1–S4: FIRST try the CONTENT-faithful path for a
            # simple, sound element shape (identity / pure-int arithmetic over the
            # loop target, over an `array int` source). Emits a per-instance
            # `list_content_comp_<n>` val carrying `Array.length result = len src`
            # /\ `forall i. result[i] = <elt[target:=src[i]]>` (or a length bound
            # for a filter). Falls through to the opaque length-only path below for
            # every unliftable element shape (seq/stmt-list/emit_ir/string/call/
            # projection with captures) — DOCUMENTED, never a false content claim.
            _content = self._content_comp(node, local_refs, invariant_ctx, subst)
            if _content is not None:
                return _content
            # list-comprehension-lowering.md L1: a comprehension `[elt for t in src (if …)]`
            # → an abstract array of the ELEMENT type with a length law (`= len src` with no
            # filter, `<= len src` with an `if`). Content is unmodeled (sound under-approx —
            # like str_split_elem_op); only the type + length matter for the emitter's
            # `ensures True` + frame contracts. @mutable_state-gated → the corpus's opaque
            # `list_comp` path is byte-identical.
            if (getattr(self, "_current_self_type", None)
                    in getattr(self, "_mutable_state_classes", set())):
                _d = node.to_dict()
                _elt = _d.get("elt", {})
                _gens = _d.get("generators", []) or []
                # IR2: bind each generator target to its iterable's element class (e.g. a
                # `sharedvar` for `sv in self.ir.get("shared_vars")`) so the element expr
                # `sv["name"]` is typed. Restored after inference (the comprehension is opaque).
                _symtab = getattr(self, "_current_symbol_table", None)
                _saved = {}
                if _symtab is not None:
                    for _g in _gens:
                        _ec = self._iter_elem_class(_g.get("iter", {}))
                        _tv = _g.get("target")
                        if _ec and isinstance(_tv, str):
                            _saved[_tv] = _symtab.get(_tv)
                            _symtab[_tv] = _ec
                # a `.to_dict()` element is an emit_ir node (to_dict is identity on the typed IR).
                _elt_todict = (isinstance(_elt, dict) and _elt.get("type") == "Call"
                               and isinstance(_elt.get("func"), str)
                               and _elt["func"].endswith(".to_dict"))
                if self._is_string_expr(_elt):                    _et = "string"
                elif _elt_todict or self._is_emit_ir_expr(_elt):  _et = "emit_ir"
                else:                                             _et = "int"
                for _tv, _old in _saved.items():
                    if _old is None: _symtab.pop(_tv, None)
                    else: _symtab[_tv] = _old
                _src = _gens[0].get("iter", {}) if _gens else {}
                _has_if = any(g.get("ifs") for g in _gens)
                _srcw = self._expr_to_whyml(_src, local_refs or set(), invariant_ctx, subst)
                # seq-model-pivot.md SQ4: `[s.to_dict() for s in <stmt-list>]` re-materialises a
                # STMT LIST — the plumbing type is `array int` (what `_stmts_to_whyml` consumes),
                # so this comprehension produces `array int` (opaque) to unify with it, over a
                # seq OR array source.
                if _elt_todict:
                    _sc = "seq 'a" if (isinstance(_src, dict) and _src.get("type") == "Var"
                                       and _src.get("name") in getattr(self, "_seq_locals", set())) else "array 'a"
                    self._add_abstract_op(f"val list_comp_stmts (src: {_sc}) : array int")
                    return f"(list_comp_stmts {_srcw})"
                # seq-model-pivot.md SQ4: over a SEQ iterable → the seq-variant comprehension
                # (`seq 'a → seq <τ>`), so the result is a pure reassignable value.
                _src_seq = (isinstance(_src, dict) and _src.get("type") == "Var"
                            and _src.get("name") in getattr(self, "_seq_locals", set()))
                _coll = "seq" if _src_seq else "array"
                _len = "Seq.length" if _src_seq else "Array.length"
                _op = f"list_comp_{'seq_' if _src_seq else ''}{_et}" + ("_filt" if _has_if else "")
                _law = "<=" if _has_if else "="
                self._add_abstract_op(
                    f"val {_op} (src: {_coll} 'a) : {_coll} {_et}\n"
                    f"    ensures {{ {_len} result {_law} {_len} src }}")
                return f"({_op} {_srcw})"
            self._add_abstract_op("val list_comp (x: int) : int")
            return "(list_comp 0)"
        if isinstance(node, SetCompExpr):
            self._add_abstract_op("val set_comp (x: int) : int")
            return "(set_comp 0)"
        if isinstance(node, DictCompExpr):
            self._add_abstract_op("val dict_comp (x: int) : int")
            return "(dict_comp 0)"

        # Non-standard-signature handlers — called explicitly
        if isinstance(node, VarExpr):      return self._handle_var_expr(node, local_refs, subst)
        if isinstance(node, FieldGetExpr): return self._handle_field_get_expr(node, invariant_ctx)

        # All other types via uniform-quad-signature dispatch
        handler = self._EXPR_DISPATCH.get(t)
        if handler:
            if handler in _TYPED_EXPR_HANDLERS:
                tn = node if not isinstance(node, OpaqueExpr) else _expr_from_dict_inner(node.raw)
                return getattr(self, handler)(tn, local_refs, invariant_ctx, subst)
            return getattr(self, handler)(expr, local_refs, invariant_ctx, subst)
        return ""

    def _expr_to_whyml_string_ctx(self, ir: Dict[str, Any], local_refs: Set[str]) -> str:
        """Emit a ghost string expression in string context (handles StrConcat, StringLiteral, ghost string vars)."""
        t = ir.get("type")
        if t == "StrConcat":
            l = self._expr_to_whyml_string_ctx(ir["left"], local_refs)
            r = self._expr_to_whyml_string_ctx(ir["right"], local_refs)
            # Why3 string.String exports 'concat' (not '^' / 'String.(^)', which is unbound) —
            # mirror _handle_strconcat_expr; `String.(^)` here made any `^` in a spec context
            # (check/ensures comparison) emit an unbound symbol.
            return f"(concat {l} {r})"
        if t == "String":
            # Mirror `_expr_to_whyml`'s String case — escape control chars/newlines
            # (this ghost-string-ctx path previously emitted the raw value with NO
            # escaping at all, so a `"` or `\` in a spec-context string would also
            # have produced invalid WhyML).
            return whyml_string_literal(ir.get("value", ""))
        if t == "Var":
            name = ir.get("name", "")
            safe = whyml_ident(name)
            if name in self._ghost_string_vars:
                return f"!{safe}"
            return safe
        # Fall back to generic emit for any other expression
        return self._expr_to_whyml(ir, local_refs)

