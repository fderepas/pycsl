from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Set

from module6_whyml.identifiers import whyml_ident
from module6_whyml.scc import sort_functions_by_scc
from module6_whyml.auto_trust import AutoTrustMixin
from module6_whyml.abstract_ops import AbstractOpsMixin
from module6_whyml.types import TypeInferenceMixin
from module6_whyml.expressions import ExpressionEmissionMixin
from module6_whyml.statements import StatementEmissionMixin
from module6_whyml.preamble import PreambleEmissionMixin
from module6_whyml.functions import FunctionEmissionMixin


class Module6_WhyMLTranspiler(
    ExpressionEmissionMixin,
    StatementEmissionMixin,
    PreambleEmissionMixin,
    FunctionEmissionMixin,
    TypeInferenceMixin,
    AutoTrustMixin,
    AbstractOpsMixin,
):
    """Reads the JSON IR and transpiles it into valid WhyML (.mlw) syntax."""

    def __init__(self, json_ir: str, memory_model: str = "hoare",
                 strict_no_exception_propagation: bool = False,
                 strict_hash_eq_consistency: bool = False,
                 check_behavioral_subtyping: bool = False) -> None:
        self.ir = json.loads(json_ir)
        self.memory_model = memory_model   # "hoare" | "typed" | "store" | "concurrent"
        # The one distinction every emission site actually makes: value-semantic arrays
        # (hoare/concurrent — arrays are values, no aliasing) vs a global heap
        # (typed/store — arrays are locations into `int_mem`/`store`). Named once here so
        # the grouping lives in a single place instead of `memory_model in (...)` at ~24
        # scattered sites. (typed-vs-store, where it matters, is the heap variable name below.)
        self._value_semantic = memory_model in ("hoare", "concurrent")
        # Layer D — emit Liskov refinement goals for overriding methods
        # (pre_base ⇒ pre_sub, post_sub ⇒ post_base). Default off.
        self.check_behavioral_subtyping = bool(check_behavioral_subtyping)
        # Workplan PR 4 — strict mode flips the ambient default at
        # call sites: unannotated callees produce a hard VC under any
        # caller that has `no_exception` set. Default off.
        self.strict_no_exception_propagation = bool(strict_no_exception_propagation)
        # Workplan PR 9 — under strict mode, the hash/eq consistency
        # property is emitted as a Why3 *goal* (must be discharged via
        # external proof). Default off — emits as an *axiom* (the user
        # is on the hook to keep the methods consistent).
        self.strict_hash_eq_consistency = bool(strict_hash_eq_consistency)
        self._abstract_ops: Dict[str, str] = {}  # Abstract val declarations: name → full decl string
        self._record_types: Dict[str, Any] = {}  # class_name_lower → {fields: [...], defaults: {...}}
        # sum-types: variant type name → {whyml_name, constructors}; constructor name →
        # {type, whyml_type, arity, payload}. Drive param typing, construction, and match.
        self._variant_types: Dict[str, Any] = {}
        self._constructors: Dict[str, Any] = {}
        self._class_constants: Dict[str, Dict[str, int]] = {}  # class_name_lower → {CONST: int literal}
        # module-constants-plan: module-level int constants (`K_IHDR = 0`) →
        # resolved to their literal in `_handle_var_expr` (body and contract).
        self._module_constants: Dict[str, int] = self.ir.get("module_constants", {})
        # inline.md Phase 1: module-level global object instances. `name → class` (orig
        # case), available in EVERY function so `g.field` resolves to the global record's
        # field (analogous to `_current_record_var_classes`, but module-scoped).
        self._module_global_classes: Dict[str, str] = {
            g["name"]: g["class"] for g in self.ir.get("module_globals", [])}
        self._ambiguous_fields: Set[str] = set()  # field names shared by >1 record → qualified labels
        self._emit_record_ctx: Optional[str] = None  # record name (lower) during invariant/witness emission
        self._shared_var_names: Set[str] = set()  # Module-level shared variable names (concurrent model)
        self._havoc_counter: int = 0             # Counter for unique havoc variable names
        self._in_spec: bool = False              # True when emitting contracts (no div-by-zero VCs)
        # Per-function state — reset per function via `_reset_function_state`;
        # initialised here so they're always defined and accessing them
        # before the first reset is safe.
        self._bounded_int: Optional[int] = None
        self._array2d_params: Set[str] = set()
        self._current_array1d_params: Set[str] = set()
        self._current_params: Set[str] = set()
        self._current_symbol_table: Dict[str, Any] = {}
        self._array_locals: Set[str] = set()
        self._dict_locals: Set[str] = set()
        self._record_locals: Set[str] = set()
        # scc3.md Phase A: quantifier-bound record vars (var → original class name),
        # registered for the duration of a `\forall o: C; …` body so `o.field` lowers
        # to the record field instead of an abstract getter. Nesting-safe (save/restore).
        self._quant_record_binders: Dict[str, str] = {}
        self._lambda_locals: Set[str] = set()
        self._current_self_type: Optional[str] = None
        self._func_return_type: str = "int"
        self._current_tuple_arity: int = 0
        self._has_early_ret: bool = False
        self._for_idx_init: str = "0"
        # Whole-module state — populated by `transpile()` before any
        # function emission; initialised empty so type-check passes and
        # accidental early access yields a clean empty default.
        self._all_record_fields: Set[str] = set()
        self._module_func_names: Set[str] = set()
        self._module_method_return_types: Dict[str, str] = {}
        self._module_method_param_types: Dict[str, List[str]] = {}
        # 1111-spec R7: per-function formal-param order + positional defaults.
        self._module_method_formal_params: Dict[str, List[str]] = {}
        self._module_method_param_defaults: Dict[str, Dict[str, Any]] = {}
        self._module_method_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._module_method_param_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._module_method_field_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        # gap7-spec-rev2: void/mutating record-method support
        self._module_method_writes: Dict[str, List[str]] = {}
        self._module_method_field_old_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._auto_trusted_array_returns: List[str] = []
        self._auto_trusted_tuple_returns: List[str] = []
        self._auto_trusted_map_returns: List[str] = []
        self._auto_trusted_set_op: List[str] = []
        # Workplan PR 4 — module-wide callee no_exception summary.
        # Populated by `transpile()` before any per-function emission.
        # Keys are function names (not whyml_ident'd). Values mirror the
        # IR's `contracts.no_exception` / `no_exception_all` /
        # `raises` fields so call sites can look them up without
        # walking the IR again.
        self._module_func_no_exception: Dict[str, Set[str]] = {}
        self._module_func_no_exception_all: Dict[str, bool] = {}
        self._module_func_raises: Dict[str, List[Dict[str, Any]]] = {}
        self._module_func_param_names: Dict[str, List[str]] = {}

    @property
    def _heap_var(self) -> str:
        """Returns the name of the mutable heap variable for the current model."""
        if self.memory_model == "typed":
            return "int_mem"
        elif self.memory_model == "store":
            return "store"
        raise ValueError(f"No heap variable in Hoare model")

    def _build_callee_no_exception_summary(self, functions: List[Dict[str, Any]]) -> None:
        """Populate the module-wide callee summary maps (workplan PR 4).
        Indexed by the IR function name (e.g. "divide_256")."""
        for func in functions:
            name = func.get("name")
            if not name:
                continue
            contracts = func.get("contracts", {})
            self._module_func_no_exception[name] = set(contracts.get("no_exception", []) or [])
            self._module_func_no_exception_all[name] = bool(
                contracts.get("no_exception_all", False))
            self._module_func_raises[name] = list(contracts.get("raises", []) or [])
            self._module_func_param_names[name] = list(func.get("formal_params", []) or [])

    def _callee_implicit_exceptions(self, callee_name: str) -> Set[str]:
        """Set of exception names the callee may raise implicitly (i.e.
        not constrained by `no_exception` or `\\all` on the callee).
        Empty in ambient mode for unannotated callees."""
        from exception_model import all_phase1_exceptions
        # Annotated callee: the callee commits to not raising these
        # exceptions. Subtracts from caller's obligation.
        proved = set(self._module_func_no_exception.get(callee_name, set()))
        if self._module_func_no_exception_all.get(callee_name, False):
            proved.update(all_phase1_exceptions())
        # Declared raises clauses constitute the callee's explicit
        # exception set. We track names only at this layer; condition
        # propagation is handled by `_wrap_call_with_callee_raises_assert`.
        declared = {r["exc_type"] for r in self._module_func_raises.get(callee_name, [])}
        return declared - proved

    def _wrap_unannotated_call_with_strict_assert(self, inner: str) -> str:
        """Strict-mode wrap for unannotated abstract callees (workplan §1.4).
        Off by default — the bare ``inner`` is returned. Under
        ``--strict-no-exception-propagation``, any call from a function
        with a `no_exception` set to an abstract/unannotated callee
        becomes an unsatisfiable assert (the user must annotate the
        callee or relax the caller).
        """
        if not self.strict_no_exception_propagation:
            return inner
        if not (self._current_no_exception or self._current_no_exception_all):
            return inner
        return f"begin assert {{ false }}; {inner} end"

    def _wrap_call_with_callee_raises_assert(self, callee_name: str,
                                              inner: str, args: List[str]) -> str:
        """For a user-function call site inside a function with
        `no_exception E`, if the callee declares `raises { E -> P }`,
        prepend `assert { not P }` and wrap the call in
        ``try ... with E -> absurd end``.

        The ``absurd`` handler turns the residual raise into a proof
        obligation of ``false`` at the exception branch — discharged
        because the assertion establishes ``not P`` and the callee's
        contract says the raise fires only when ``P``.
        """
        active = set(self._current_no_exception)
        if self._current_no_exception_all:
            from exception_model import all_phase1_exceptions
            active.update(all_phase1_exceptions())
        if not active:
            return inner
        raises = self._module_func_raises.get(callee_name, [])
        if not raises:
            return inner
        asserts: List[str] = []
        handlers: List[str] = []
        param_names = self._module_func_param_names.get(callee_name, [])
        for r in raises:
            exc = r.get("exc_type")
            if exc not in active:
                continue
            cond_ir = r.get("condition")
            cond_str = self._render_callee_condition(cond_ir, param_names, args)
            if cond_str is None:
                asserts.append("assert { false };")
            else:
                asserts.append(f"assert {{ not ({cond_str}) }};")
            handlers.append(f"{exc} -> absurd")
        if not asserts:
            return inner
        # `try CALL with E1 -> absurd | E2 -> absurd end` — the
        # try/with discharges the effect typing; `absurd` discharges
        # the unreachable branch using the assertion.
        wrapped = f"try {inner} with {' | '.join(handlers)} end"
        return f"begin {' '.join(asserts)} {wrapped} end"

    def _render_callee_condition(self, cond_ir: Any,
                                  param_names: List[str],
                                  args: List[str]) -> Optional[str]:
        """Render a callee `raises` condition into a WhyML expression in
        the caller's scope, substituting actual args for callee param
        names. Returns None if the IR shape is not supported."""
        if cond_ir is None or not param_names:
            return None
        subst = {p: a for p, a in zip(param_names, args)}
        try:
            # Reuse the existing expression renderer with a substitution
            # map — this preserves the callee's contract semantics while
            # binding parameters to the caller's arg strings.
            return self._expr_to_whyml(cond_ir, set(), invariant_ctx=False, subst=subst)
        except Exception:
            return None

    def _wrap_with_no_exception_assert(self, op_key, operands, inner_expr: str) -> str:
        """Wrap ``inner_expr`` with a no_exception assertion if appropriate.

        ``inner_expr`` is the WhyML rendering of the original operation.
        If the current function declares ``no_exception E`` for an
        exception triggered by ``op_key``, the returned string prepends a
        ``begin assert { ... }; inner_expr end`` block. Otherwise returns
        ``inner_expr`` unchanged.

        Wrap only at expression sites that emit body code — the helper
        early-exits in spec context and when no trigger applies, so
        callers can wrap unconditionally.
        """
        pred = self._maybe_emit_no_exception_assert(op_key, operands)
        if not pred:
            return inner_expr
        # `begin S1; S2 end` is the WhyML expression-sequence form. The
        # `assert` is unit-typed; the parenthesised whole reduces to the
        # value of ``inner_expr``.
        return f"begin {pred} {inner_expr} end"

    def _maybe_emit_no_exception_assert(self, op_key, operands) -> str:
        """Single chokepoint for `no_exception` VC injection.

        `op_key` is a (kind, subkind) tuple matching
        `exception_model.TRIGGERS` (e.g. ("binop", "/")). `operands` is a
        list/tuple of WhyML strings substituted positionally into the
        trigger template ({0}, {1}, ...).

        Returns the WhyML assertion fragment (without trailing newline /
        indentation — the caller is responsible for inserting it into a
        statement context). Returns "" when no assertion should fire:
        either the function has no `no_exception` context, or the
        operation is being emitted inside a contract (`_in_spec`), or the
        operation does not match any trigger.

        Workplan PR 3. See `exception_model.TRIGGERS` for the table.
        """
        # Contract-context emission must not trigger VC injection.
        if getattr(self, "_in_spec", False):
            return ""
        # No per-function context → nothing to do (preserves backward
        # compat for unannotated functions per workplan §11.3).
        if not getattr(self, "_current_no_exception", set()) \
           and not getattr(self, "_current_no_exception_all", False):
            return ""
        from exception_model import triggers_for, all_phase1_exceptions
        triggers = triggers_for(op_key)
        if not triggers:
            return ""
        active = set(self._current_no_exception)
        if self._current_no_exception_all:
            active.update(all_phase1_exceptions())
        parts: List[str] = []
        for exc_name, template in triggers:
            if exc_name not in active:
                continue
            # Placeholder triggers (e.g. .index, next) emit `true`; skip
            # them — `assert { true }` is a useless VC.
            if template.strip() == "true":
                continue
            expr = template.format(*[str(o) for o in operands])
            parts.append(f"assert {{ {expr} }};")
        return " ".join(parts)

    _EXPR_DISPATCH: Dict[str, str] = {
        "BinOp":        "_handle_binop",
        "Call":         "_handle_call_expr",
        "Subscript":    "_handle_subscript",
        "Attribute":    "_handle_attribute_expr",
        "FString":      "_handle_fstring_expr",
        "UnaryOp":      "_handle_unaryop_expr",
        "Old":          "_handle_old_expr",
        "At":           "_handle_at_expr",
        "IfExpr":       "_handle_ifexpr_expr",
        "NamedExpr":    "_handle_named_expr_expr",
        "SliceAccess":  "_handle_slice_access_expr",
        "ArrayLen":     "_handle_arraylen_expr",
        "InGlobals":    "_handle_in_globals_expr",
        "InScope":      "_handle_in_scope_expr",
        "Valid":        "_handle_valid_expr",
        "Separated":    "_handle_separated_expr",
        "Length2D":     "_handle_length2d_expr",
        "Valid2D":      "_handle_valid2d_expr",
        "IsSorted":     "_handle_issorted_expr",
        "ArrayEq":      "_handle_arrayeq_expr",
        "Permutation":  "_handle_permutation_expr",
        "Sum":          "_handle_sum_node_expr",
        "Lambda":       "_handle_lambda_expr",
        "SetLit":       "_handle_setlit_expr",
        # Ghost expression types
        "MkTuple":      "_handle_mktuple_expr",
        "FstExpr":      "_handle_fst_expr",
        "SndExpr":      "_handle_snd_expr",
        "ProjExpr":     "_handle_proj_expr",
        "CtorTest":     "_handle_ctor_test_expr",
        "CtorPayload":  "_handle_ctor_payload_expr",
        "StrConcat":    "_handle_strconcat_expr",
        "StrLength":    "_handle_str_length_expr",
        "StrSub":       "_handle_str_sub_expr",
        "GhostCopy":      "_handle_ghost_copy_expr",
        "GhostCopyRange": "_handle_ghost_copy_range_expr",
        "GhostMake":      "_handle_ghost_make_expr",
        "MapEmpty":     "_handle_map_empty_expr",
        "MapGet":       "_handle_map_get_expr",
        "MapSet":       "_handle_map_set_expr",
        "MapEq":        "_handle_map_eq_expr",
        "HasKey":       "_handle_has_key_expr",
        "MapRemove":    "_handle_map_remove_expr",
        "SetEmpty":     "_handle_set_empty_expr",
        "SetAdd":       "_handle_set_add_expr",
        "SetRemove":    "_handle_set_remove_expr",
        "SetMem":       "_handle_set_mem_expr",
        "SetUnion":     "_handle_set_union_expr",
        "SetInter":     "_handle_set_inter_expr",
        "SetDiff":      "_handle_set_diff_expr",
        "SetCard":      "_handle_set_card_expr",
        "SetSubset":    "_handle_set_subset_expr",
        "SetEq":        "_handle_set_eq_expr",
        "Nil":          "_handle_nil_expr",
        "Cons":         "_handle_cons_expr",
        "Hd":           "_handle_hd_expr",
        "Tl":           "_handle_tl_expr",
        "ListLength":   "_handle_list_length_expr",
        "Nth":          "_handle_nth_expr",
        "Mem":          "_handle_mem_expr",
        "Append":       "_handle_append_expr",
    }

    def transpile(self) -> str:
        """Entry point: converts the entire program to a .mlw string."""
        functions = self.ir.get("functions", [])
        type_decls = self.ir.get("type_decls", [])
        all_bodies = [func["body"] for func in functions]

        self._all_record_fields = self._collect_record_fields(type_decls)

        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs)
        out += self._emit_shared_state()

        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines

        # inductive.md: `#@ inductive` predicates emit AFTER datatypes (their rules
        # reference constructors) and BEFORE axioms/functions (which may mention the
        # predicate in contracts). Empty for non-inductive modules → no change.
        # Register the predicate names FIRST so the rule clauses' own `p(args)`
        # applications lower to `(p args)` (not an abstract op).
        self._inductive_preds = (
            {ind["name"] for ind in self.ir.get("inductive_decls", [])}
            | {m["name"] for ind in self.ir.get("inductive_decls", [])
               for m in ind.get("members", [])})   # P2: mutual `with` group members
        out += self._emit_inductive_decls(self.ir.get("inductive_decls", []))

        # `#@ proof` axioms go AFTER the type declarations so an axiom may
        # quantify over a user `#@ datatype` (A4 json round-trip). Also sets
        # `self._axiom_emitted_decls` for the abstract-val dedup (which runs
        # at the end via `_insert_abstract_val_block`).
        out += self._emit_preamble_axioms(self.ir)

        # inline.md Phase 1: module-level global object instances. Emitted AFTER the
        # record type declarations (so `_record_types` is populated and the constructor
        # literal + type invariant resolve) and BEFORE functions (which reference `g`).
        out += self._emit_module_globals()

        self._emit_opaque_class_aliases(functions, out, declared_types)

        self._module_func_names = {whyml_ident(func["name"]) for func in functions}
        # Stateful composition: the set of flattened provider methods (`<composer>__<m>`,
        # from `_apply_composition`). A `self.<m>()` call inside the composer resolves to
        # the concrete provider (passing `self`) instead of an abstract `val`, so the
        # provider's state-mutating contract reaches the composer. Empty for non-mixin
        # modules → self-calls keep their abstract-val lowering → byte-identical.
        self._composed_provider_methods = set(self.ir.get("composed_provider_methods", []))
        # inductive.md: declared inductive-predicate names, so a `p(args)` application
        # in a contract / rule lowers to `(p args)` (not an arity-suffixed abstract op).
        self._inductive_preds = (
            {ind["name"] for ind in self.ir.get("inductive_decls", [])}
            | {m["name"] for ind in self.ir.get("inductive_decls", [])
               for m in ind.get("members", [])})   # P2: mutual `with` group members
        # Mixin verify-once (S1): synthesize a pseudo-function per declared
        # `depends_method`/`requires_method` so the SAME contract-propagation maps
        # that wire `self.<m>(…)` to a sibling's `ensures` also carry the DECLARED
        # interface's contract. The pseudo-funcs feed only the lookup maps below —
        # never the emission list — so the abstract `self.<dep>` val picks up the
        # dependency's `ensures` (e.g. `result >= 0`) and the provider verifies once
        # against it. Empty for non-mixin modules → maps unchanged → byte-identical.
        funcs_for_maps = functions + self._mixin_dep_pseudo_functions(functions)
        self._module_method_return_types = self._build_method_return_type_map(funcs_for_maps)
        self._module_method_param_types = self._build_method_param_types_map(funcs_for_maps)
        # 1111-spec R7: formal-param order + positional defaults, for call-site
        # default fill of cross-module / module-function calls.
        self._module_method_formal_params = {
            f["name"]: list(f.get("formal_params", [])) for f in funcs_for_maps}
        self._module_method_param_defaults = {
            f["name"]: dict(f.get("param_defaults", {})) for f in funcs_for_maps}
        self._module_method_result_ensures = self._build_method_result_ensures_map(funcs_for_maps)
        self._module_method_param_result_ensures = self._build_method_param_result_ensures_map(funcs_for_maps)
        self._module_method_field_result_ensures = self._build_method_field_result_ensures_map(funcs_for_maps)
        # gap7-spec-rev2: void/mutating record-method support. `_writes` = self-fields a method
        # `assigns`; `_field_old_ensures` = its `ensures` over self-fields + `\old(self.f)` (no
        # \result/param). Both derived from the SAME `contracts.*` the method's `let` is verified
        # against (O2 — cannot drift). A method may appear in BOTH field_result and field_old maps.
        self._module_method_writes = self._build_method_writes_map(funcs_for_maps)
        self._module_method_field_old_ensures = self._build_method_field_old_ensures_map(funcs_for_maps)
        # The pseudo-funcs have empty bodies, so the return-type map derives `unit`
        # for a scalar dependency; override with the type from the declared signature
        # so `self.<dep>(…)` is a `: int` (etc.) call, not `: unit`.
        for pf in self._mixin_dep_pseudo_functions(functions):
            self._module_method_return_types[pf["name"]] = pf["_mixin_ret_whyml"]
        self._build_callee_no_exception_summary(functions)

        sorted_functions, scc_info = sort_functions_by_scc(functions)
        for func in sorted_functions:
            out += self._emit_function(func, scc_info)

        if self.check_behavioral_subtyping:
            out += self._emit_subtyping_goals(functions)

        out.append("end")
        self._insert_abstract_val_block(out)
        return "\n".join(out)
