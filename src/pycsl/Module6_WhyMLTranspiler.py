from __future__ import annotations

import json
import re
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


# parser-primitives-wall-impl-3.md capability (i): the internal sentinel that parks
# the emit_ir ADT theory's position while the rest of the file is emitted. It NEVER
# survives `transpile` (`_resolve_deferred_exprir_theory` either replaces it with the
# theory or deletes it).
_EXPRIR_THEORY_SLOT = "(*__pycsl_exprir_theory_slot__*)"


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
        # cleared-array item 1 (call comprehensions): the set of module functions
        # already emitted as a pure `let [rec] function` (a logic symbol usable in a
        # contract term). Populated in `_emit_function` as each function is emitted
        # (callee-before-caller SCC order), so a comprehension `[g(x) for x in a]`
        # processed during the CALLER's body can check `g` is spec-callable.
        self._emitted_logic_funcs: Set[str] = set()
        # cleared-array item 1: content-comp `val`s whose `ensures` references a USER
        # `let function` (a call comprehension). Such a `val` must be declared AFTER
        # its referenced function, so it is deferred here as (op_name, decl,
        # using_func) and spliced in just before the using function's `let` line by
        # `_insert_late_content_ops`, instead of into the early abstract-op block.
        self._late_content_ops: List[Any] = []
        self._record_types: Dict[str, Any] = {}  # class_name_lower → {fields: [...], defaults: {...}}
        # sum-types: variant type name → {whyml_name, constructors}; constructor name →
        # {type, whyml_type, arity, payload}. Drive param typing, construction, and match.
        self._variant_types: Dict[str, Any] = {}
        self._constructors: Dict[str, Any] = {}
        self._class_constants: Dict[str, Dict[str, int]] = {}  # class_name_lower → {CONST: int literal}
        # 7b (self-tcb-reduction L4b): class_name → {CONST: [str-member, ...]} for class-body
        # string-SET constants (`_GENERIC_BASE_NAMES = {"Generic"}`); feeds the faithful
        # `<x> in self.<CONST>` -> `str_eq_op` disjunction membership.
        self._class_str_set_constants: Dict[str, Dict[str, List[str]]] = {}
        # module-constants-plan: module-level int constants (`K_IHDR = 0`) →
        # resolved to their literal in `_handle_var_expr` (body and contract).
        self._module_constants: Dict[str, int] = self.ir.get("module_constants", {})
        # module-const-dict-get: module-level constant str->str dict literals
        # (`OP_MAP = {"==":"=", ...}`) → recognized at `NAME.get(k, default)` in
        # `_lower_dict_get_call` as a chained string if-then-else. Empty for every
        # existing corpus program (byte-identical emission).
        self._module_const_dicts: Dict[str, Dict[str, str]] = self.ir.get("module_const_dicts", {})
        # compound-key const-map lowering: `{NAME: {"key_whyml":…, "elem_whyml":…}}`
        # for a module-const dict with a tuple key + list value (`TRIGGERS`). Each
        # becomes an opaque `val constant NAME : map <key> (option (list <elem>))`
        # (emitted after the type decls) and a `NAME.get(k, [])` read lowers to the
        # faithful defaulting `Map.get` in `_lower_dict_get_call`. Empty for every
        # corpus program (byte-identical emission).
        self._module_const_compound_dicts: Dict[str, Dict[str, str]] = self.ir.get(
            "module_const_compound_dicts", {})
        # gap-9: signatures of imported `#@ inductive` predicates whose RULE was
        # NOT crossed (kept opaque to avoid an E-matching blow-up). Lets the
        # `_emit_contract_logic_symbol` fallback declare the opaque predicate
        # with the correct param types (e.g. `name_present (array int) string`).
        self._imported_inductive_sigs: Dict[str, str] = self.ir.get(
            "_imported_inductive_sigs", {})
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
        self._emitting_val_contract: bool = False  # 11-0632-spec-8 Part 2: True only while emitting a bodyless val/trusted-stub contract
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
        # body-gate gap-5: SCALAR (int/bool/…) quantifier binders, registered for the
        # duration of a `\forall k; …` body so `k` reads BARE even when a same-named
        # loop/local var is in `local_refs` (e.g. sys_unlink's `for k in …` loop var
        # shadowed by the uniqueness `#@ assert \forall k`). Else `k` lowered to `!k`.
        self._quant_scalar_binders: Set[str] = set()
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
        # wrong-lowering-to-fix.md §WL-05b: func-name -> caller-visible mutable
        # `ref (map …)` dict/set param names (fixpoint). Empty default → byte-identical.
        self._func_mutated_collection_params: Dict[str, Set[str]] = {}
        # stmt-list-append-mutation wall (C-bucket): func-name -> caller-visible mutable
        # `ref (seq stmt_ir)` list param names (fixpoint). Empty default → byte-identical.
        self._func_stmt_seq_mut_params: Dict[str, Set[str]] = {}
        # 10-1732-gap (Gaps 2/3): callee return-annotation + by-name param WhyML types.
        self._module_method_return_annotations: Dict[str, str] = {}
        self._module_method_param_whyml_types: Dict[str, Dict[str, str]] = {}
        # 1111-spec R7: per-function formal-param order + positional defaults.
        self._module_method_formal_params: Dict[str, List[str]] = {}
        self._module_method_param_defaults: Dict[str, Dict[str, Any]] = {}
        self._module_method_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._module_method_param_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._module_method_field_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        # gap-9 (A2c+): ensures over \result + self-fields + params (params renamed).
        self._module_method_field_param_result_ensures: Dict[str, List[Dict[str, Any]]] = {}
        # gap7-spec-rev2: void/mutating record-method support
        self._module_method_writes: Dict[str, List[str]] = {}
        self._module_method_field_old_ensures: Dict[str, List[Dict[str, Any]]] = {}
        # void-mutator NON-QUANTIFIED write postconditions: self-field + params (no \result,
        # no \old, no quantifier) — the _zero_entry/_write_entry write-posts the six maps drop.
        # Safe to expose (no quantifier → no trigger → no E-matching poison).
        self._module_method_field_param_post_ensures: Dict[str, List[Dict[str, Any]]] = {}
        # M4: QUANTIFIED self-field frame ensures, opt-in per `#@ propagate_frame` callee
        # (e.g. _zero_entry). Lowered with a specific Call-trigger so they don't poison.
        self._module_method_field_param_frame_ensures: Dict[str, List[Dict[str, Any]]] = {}
        self._frame_trigger_active: bool = False
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
        self._mutable_state_classes = {
            whyml_ident(td["name"].lower()) for td in type_decls
            if isinstance(td, dict) and td.get("kind") == "record" and td.get("mutable_state")
        } | {
            # gating fix (self-tcb-reduction): a @mutable_state class with no fields/bases
            # never gets a "record" type_decl (Module5's `fields or bases` gate — a WhyML
            # record cannot carry zero fields), so it would never reach the set above even
            # though it IS @mutable_state-decorated. `mutable_state_class_names` is the
            # unconditional AST-level registration (Module5_IREmitter.visit_ClassDef) —
            # class-set membership, not method-name or record-population dependent. Empty
            # for every module with no such stateless-but-decorated class → byte-identical.
            whyml_ident(n.lower()) for n in self.ir.get("mutable_state_class_names", [])
        }
        # WL-04b (wrong-lowering-to-fix.md §WL-04 record residual): record CLASS names
        # (type_decls keys) used as a flat `List[<record>]` ELEMENT, so `_emit_type_decls`
        # emits them PURE (Why3 forbids a mutable element inside `array`). Empty for
        # every module with no `List[<record>]` param/return → byte-identical.
        self._list_element_record_types: Set[str] = set(
            self.ir.get("list_element_record_types", []))

        # tier3-p1 T3.1.1: an IR-node-typed param/local (`node: ExprIR`) makes the
        # emitter reflect on it as the `emit_ir` ADT (functions.py::_param_type_str →
        # `emit_ir`), so the ADT theory (variant type + projections + `size` recursion
        # measure) MUST be in scope — even without a @mutable_state class. Scan every
        # function's symbol_table for an IR-node base name. Corpus programs annotate no
        # param/local with these names → flag False → theory NOT emitted → byte-identical.
        _IRNODE_TAGS = ("ExprIR", "StmtIR", "IRNode", "ContractExprIR", "exprir", "emit_ir")
        self._uses_ir_node_param = any(
            v in _IRNODE_TAGS
            for f in functions
            for v in (f.get("symbol_table", {}) or {}).values()
        )

        # module-emission.md: OPT-IN axiom isolation. If a function carries
        # `#@ verify_module <name>` AND is emitted here as a REAL `let` body (i.e. it is
        # verified in THIS unit — not an imported/`\trusted` stub, and not inlined away),
        # emit each named group into its OWN top-level Why3 `module` (shared infra
        # re-declared, per-module axiom selection) so the cited `#@ proof` axioms of one
        # group are NOT in scope for another's goals. The split's whole purpose is to
        # isolate the SMT context of a function's BODY VC; an importer that pulls the
        # tagged function in as a trusted stub gains nothing from the split (it never
        # proves that body) and the cross-module `clone`-refinement has no real `let` to
        # discharge it — so for an importer the tag is inert and we take the flat path
        # (which keeps every importer byte-identical). Default (no real-body tag) → the
        # single flat `module PyCSL_Program`, byte-identical. (Why3 `scope` does NOT
        # isolate axioms — a scope is a namespace; only separate `module`s do; spike
        # `getting-better/20260620-0640-scope-emission-milestone0-YES.md`.)
        if any(f.get("verify_module") and not f.get("trusted") and not f.get("abstract")
               for f in functions):
            return self._transpile_modular(functions, type_decls)

        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs)
        out += self._emit_shared_state()

        # gap-12 Wall A part 1: populate `_axiom_logic_funcs` BEFORE
        # `_emit_type_decls` so a `#@ class invariant` that applies an axiom
        # function (`slot_inode`/`slot_name`/`dir_lookup`) lowers it to the raw
        # bound application `(f args)` instead of an unbound arity-suffixed
        # abstract op (`slot_inode_3`). Idempotent (re-run at L407+ and inside
        # `_emit_preamble_axioms`), so a file whose invariants don't apply an
        # axiom func is unaffected → byte-identical.
        self._precompute_axiom_logic_funcs(self.ir)

        # gap-12 Wall A part 2: when a class invariant references an axiom
        # function, emit the matching `val function` decls BEFORE the record type
        # that names them (else the `invariant { ... slot_inode ... }` references
        # symbols declared later in the file → unbound). GATED by
        # `_class_inv_refs_axiom_func` (mirroring the gap-9 conditional reorder):
        # False for the whole existing corpus (os's 13 class invariants reference
        # only `\length`/`self.disk[i]`/scalars), so nothing reorders and the
        # type-decl emission stays byte-identical. The dedup via
        # `_axiom_emitted_decls` keeps the later `_emit_preamble_axioms` /
        # `_emit_uncited_axiom_func_decls` from re-declaring these symbols.
        if self._class_inv_refs_axiom_func(self.ir):
            out += self._emit_uncited_axiom_func_decls()
            # gap-13 Wall E/M: a class-invariant axiom (an axiom that CONSTRAINS
            # the axiom-func symbols the invariant applies — e.g.
            # `UnixFs.Dir.empty_disk_slots_dead` / `block5_decode_frame`) must be
            # in scope at the RECORD's `by`-witness VC and at every method's
            # type-invariant VC. A Why3 `axiom` only constrains its symbols from
            # its point of declaration ONWARD, so emitting it after the record (the
            # historical position) leaves the establishment VC unable to see it
            # (gap-13: `unixinodefilesystem'vc` Unknown). Hoist those axioms HERE,
            # before the record, and record them so `_emit_preamble_axioms` does
            # not re-emit them. Same `_class_inv_refs_axiom_func` gate → False for
            # the whole existing corpus, so emission stays byte-identical there.
            out += self._emit_class_inv_axioms(self.ir)

        # typed-ir-for-b-ceiling.md B-C1/B-C2: the `emit_ir` ADT + projections BEFORE
        # the record types — an ExprIR-valued field names `emit_ir`, so the ADT must be
        # in scope first. Gated on a @mutable_state class OR (tier3-p1) an IR-node-typed
        # param/local; corpus has neither → byte-identical.
        if (getattr(self, "_mutable_state_classes", None)
                or getattr(self, "_uses_ir_node_param", False)
                or self._uses_stmt_ir()
                or self._uses_call_kw()
                # L1: the tparam theory references emit_ir (the bound child) + reuses
                # is_var/is_attribute/name_of → needs the full emit_ir theory. Gated on
                # `_uses_tparam` (TParamNode sentinel) → byte-inert elsewhere.
                or self._uses_tparam()):
            # theory-tailoring: emit the MINIMAL emit_ir surface for opaque-use
            # emitter mirrors, gated by an EXPLICIT class-name ALLOW-LIST
            # (`_TAILOR_OPAQUE_MIRROR_CLASSES`). These mirrors pass emit_ir
            # purely opaquely (no ctor construction / no projection in any
            # proven body), so only the bare `type emit_ir` need exist — the
            # ~80-ctor theory (kind_of/size/projectors/lemmas/irlist/iropt) is
            # dropped, keeping every VC's SMT context small (~4x faster proof).
            # Corpus programs NEVER define these emitter mixin classes, so the
            # tailoring is corpus-inert BY CONSTRUCTION (full theory kept /
            # byte-identical there). The allow-list is matched against the
            # file's @mutable_state class names (the reliable AST-level
            # registration from Module5_IREmitter.visit_ClassDef) — NOT a
            # post-hoc emitted-body symbol scan (which mis-classified corpus +
            # monomorphize in a prior attempt). See preamble.py.
            # Only `StatementEmissionMixin` (statements.py) is TRULY opaque:
            # its proven bodies never construct/project a rich emit_ir symbol,
            # so the minimal surface typechecks + proves (verified). NOTE:
            # `ControlFlowStmtMixin` (stmt_control_flow.py) is NOT opaque — its
            # bodies apply `svalue_of` (a rich projector), so it must keep the
            # FULL theory (a minimal surface fails with `unbound ... svalue_of`);
            # it is deliberately excluded from the allow-list.
            _TAILOR_OPAQUE_MIRROR_CLASSES = {"StatementEmissionMixin"}
            if set(self.ir.get("mutable_state_class_names", [])) & _TAILOR_OPAQUE_MIRROR_CLASSES:
                _exprir_theory = self._emit_minimal_emit_ir_theory()
            else:
                _exprir_theory = self._emit_exprir_theory()
            # Return_emit_ir infra: an emit_ir-returning function's early-return catch
            # (`_wrap_body_with_return_catch`) needs this exception — it must be declared
            # AFTER the `emit_ir` ADT (just emitted above) since it carries an `emit_ir`
            # payload, so it cannot live in `_emit_preamble_exceptions` (which runs before
            # the ADT is in scope). `needs_return_emit_ir` is False for the whole existing
            # corpus (no emit_ir-returning function has an early/in-loop return there yet)
            # → inert.
            if needs.get("needs_return_emit_ir"):
                _exprir_theory = list(_exprir_theory) + [
                    "", "  exception Return_emit_ir emit_ir"]
            # parser-primitives-wall-impl-3.md capability (i) — LOW-BLAST-RADIUS
            # record-element class-field gate. `_mutable_state_classes` is the COARSE
            # disjunct above: it fires for ANY @mutable_state class, including one whose
            # state is plain records/arrays/ints (a `_Parser`-shaped token cursor) and
            # that never names an emit_ir symbol. Emitting the ~277-line ADT theory there
            # is what made `@mutable_state` unaffordable on a big mirror file (round 2's
            # measured +283 lines / CERTIFIED-BOUNDARY). The four NARROW disjuncts
            # (IR-node param, stmt_ir, call_kw, tparam) are positive evidence of real
            # emit_ir use, so they emit eagerly and are untouched. When ONLY the coarse
            # disjunct fires we DEFER: park a sentinel, emit the rest of the file, and
            # splice the theory back in iff the emitted text actually references a symbol
            # the theory declares (`_resolve_deferred_exprir_theory`). Any reference —
            # including one inside a comment — re-inserts, so the decision is
            # conservative in the safe direction and every file that uses emit_ir stays
            # BYTE-IDENTICAL. Only a @mutable_state class with zero emit_ir contact loses
            # the theory (and it could not have used it anyway).
            if (getattr(self, "_uses_ir_node_param", False)
                    or self._uses_stmt_ir()
                    or self._uses_call_kw()
                    or self._uses_tparam()):
                out += _exprir_theory
            else:
                self._exprir_deferred = (_EXPRIR_THEORY_SLOT, list(_exprir_theory))
                out.append(_EXPRIR_THEORY_SLOT)

        # pyval-value-model-wall (self-tcb-reduction, Tier-5 heterogeneous value model):
        # emit the certified `hval` sum + `hval_list` BEFORE the record types — a
        # `Dict[str, PyVal]` field/local names `pyval`, so the ADT must be in scope first.
        # Gated on `_uses_pyval` (a `Dict[str, PyVal]` annotation is present); the corpus
        # has none → byte-identical there. Co-landed with the Phase2f_PyVal cert.
        if self._uses_pyval():
            out += self._emit_pyval_theory()

        # set-value-model-wall (self-tcb-reduction, Tier-5 value-model wall): the
        # executable emitter-local `Set[str]` value model — a `set.SetApp[string]`
        # clone in a nested `scope StrSet`. Emitted BEFORE the record types (a
        # `Set[str]` local names `StrSet.set`). Gated on `_uses_str_set` (a
        # `Set[str] = set()` local is present); the corpus has none -> byte-identical.
        if self._uses_str_set():
            out += self._emit_str_set_theory()

        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines
        # value-model campaign incr5 (primitive c): declare `Return_<variant>` exceptions HERE —
        # after the synthesized `_union_*` types are in scope — for early-returning Optional[X]
        # walkers. Empty (byte-identical) for modules with none.
        out += self._emit_union_return_exceptions(needs, declared_types)
        out += self._emit_module_const_compound_maps()

        # inductive.md: `#@ inductive` predicates emit AFTER datatypes (their rules
        # reference constructors) and BEFORE axioms/functions (which may mention the
        # predicate in contracts). Empty for non-inductive modules → no change.
        # Register the predicate names FIRST so the rule clauses' own `p(args)`
        # applications lower to `(p args)` (not an abstract op).
        self._inductive_preds = (
            {ind["name"] for ind in self.ir.get("inductive_decls", [])}
            | {m["name"] for ind in self.ir.get("inductive_decls", [])
               for m in ind.get("members", [])})   # P2: mutual `with` group members
        # Precompute the axiom-backing logic-function names (e.g.
        # `slot_inode`/`slot_name`/`dir_lookup`) BEFORE inductive emission, so a
        # `#@ inductive` rule that applies one of them (the `present` /
        # `name_present` body) lowers to the raw bound application, not an
        # abstract op.
        self._precompute_axiom_logic_funcs(self.ir)

        # gap-9: an `#@ inductive` rule may reference an axiom-backing logic
        # function (`dir_lookup`) AND/OR a module-level global (`_filesystem`),
        # which must be in scope BEFORE the inductive block. ONLY in that case
        # do we reorder to axioms → globals → inductive; otherwise keep the
        # historical inductive → axioms → globals order so every existing
        # inductive/axiom file emits byte-identically.
        if self._inductive_refs_global_or_axiom_func(self.ir):
            out += self._emit_preamble_axioms(self.ir)
            out += self._emit_uncited_axiom_func_decls()
            out += self._emit_module_globals()
            out += self._emit_inductive_decls(self.ir.get("inductive_decls", []))
        else:
            out += self._emit_inductive_decls(self.ir.get("inductive_decls", []))
            # `#@ proof` axioms go after type declarations so an axiom may
            # quantify over a user `#@ datatype` (A4 json round-trip); also sets
            # `self._axiom_emitted_decls` for the abstract-val dedup.
            out += self._emit_preamble_axioms(self.ir)
            out += self._emit_uncited_axiom_func_decls()
            # inline.md Phase 1: module-level global object instances. Emitted
            # AFTER the record type declarations and BEFORE functions.
            out += self._emit_module_globals()

        self._emit_opaque_class_aliases(functions, out, declared_types)

        self._module_func_names = {whyml_ident(func["name"]) for func in functions}
        # allocator-frame plan §2.7: methods that OPTED IN to concrete sibling-calls via
        # `#@ sibling_concrete`. A `self.<m>()` call to one of these lowers to a CONCRETE
        # call (the callee's real contract + type-invariant guarantee reaches the caller);
        # every other self-call keeps the default abstract-`val` stub. Default-empty -> no
        # module without the marker is affected (byte-identical).
        self._sibling_concrete_methods = {whyml_ident(func["name"]) for func in functions
                                          if func.get("sibling_concrete")}
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
        # wrong-lowering-to-fix.md §WL-05b: func-name -> {dict/set params modelled as a
        # caller-visible mutable `ref (map ...)` (fixpoint over direct item-mutation +
        # transitive param forwarding). Consulted at call sites (pass the bare ref) and
        # in `_reset_function_state` (ref param type + `writes` frame). Empty for every
        # read-only-collection program -> byte-identical.
        self._func_mutated_collection_params = \
            self._build_func_mutated_collection_params(funcs_for_maps)
        # stmt-list-append-mutation wall (C-bucket): func-name -> list params modelled as
        # a caller-visible mutable `ref (seq stmt_ir)` (fixpoint over direct stmt-append +
        # transitive param forwarding). Empty for every program with no `{"stmt":K}`
        # append -> byte-identical.
        self._func_stmt_seq_mut_params = \
            self._build_func_stmt_seq_mut_params(funcs_for_maps)
        # 1111-spec R7: formal-param order + positional defaults, for call-site
        # default fill of cross-module / module-function calls.
        self._module_method_formal_params = {
            f["name"]: list(f.get("formal_params", [])) for f in funcs_for_maps}
        self._module_method_param_defaults = {
            f["name"]: dict(f.get("param_defaults", {})) for f in funcs_for_maps}
        # 10-1732-gap (Gap 3): by-name {param → WhyML type} for call-site default fill,
        # so an omitted `None`-defaulted non-int param is filled at its faithful zero
        # (`""`/`0.0`) instead of int `0`. Built from the SAME `funcs_for_maps` (incl.
        # injected imported `\trusted` stubs), so imported callees are covered.
        self._module_method_param_whyml_types = \
            self._build_method_param_whyml_types_by_name(funcs_for_maps)
        # 10-1732-gap (Gap 2): callee-name → Python `return_annotation` (e.g. "str").
        # NOTE (deviation from spec R1, which assumed `_module_method_return_types`
        # already carried "string" for a `-> str` callee): it does NOT — that map is
        # `_build_method_return_type_map`, a stripped duplicate of `_compute_return_type`
        # that maps only list/set/dict, leaving `-> str` as "int" (ir_scanner
        # find_return_type even maps a String literal to "int"). Mutating that shared map
        # to add the str case would risk the byte output of its many dotted-call/abstract-
        # val consumers (expressions.py:724/762/764, stmt_control_flow.py:152/157). So
        # Gap 2 keys on this SEPARATE annotation map (the pre-written, previously-unwired
        # `_build_method_return_annotation_map`), which touches NO existing consumer —
        # zero byte risk. Built from `funcs_for_maps`, so imported str-stubs are covered.
        self._module_method_return_annotations = \
            self._build_method_return_annotation_map(funcs_for_maps)
        # str-list-elements: the set of module functions that return a STRING-element list
        # (`array string`, via a returned seq local whose `seq_value_types` is "string").
        # A caller binding `names = f(...)` for such an `f` gets a string-element array
        # local, so `names[i]` reads a `string` (feeding a string-typed callee like
        # sys_stat). Empty for every module with no string lists → byte-identical.
        self._module_string_seq_funcs = {
            f["name"] for f in funcs_for_maps
            if self._func_returns_string_seq(f)
        }
        self._module_method_result_ensures = self._build_method_result_ensures_map(funcs_for_maps)
        self._module_method_param_result_ensures = self._build_method_param_result_ensures_map(funcs_for_maps)
        self._module_method_field_result_ensures = self._build_method_field_result_ensures_map(funcs_for_maps)
        # gap-9 (A2c+): ensures referencing `\result` + self-fields + params
        # (the os syscalls' `(\result==0) <==> dir_lookup(self.disk, 5, pathname)
        # >= 0`). Closes the last A2c gap — a clause mixing a self-field AND a
        # param previously propagated nowhere. Params are renamed to `x_i`; the
        # receiver stays `self` (distinct namespace, no collision).
        self._module_method_field_param_result_ensures = \
            self._build_method_field_param_result_ensures_map(funcs_for_maps)
        # gap7-spec-rev2: void/mutating record-method support. `_writes` = self-fields a method
        # `assigns`; `_field_old_ensures` = its `ensures` over self-fields + `\old(self.f)` (no
        # \result/param). Both derived from the SAME `contracts.*` the method's `let` is verified
        # against (O2 — cannot drift). A method may appear in BOTH field_result and field_old maps.
        self._module_method_writes = self._build_method_writes_map(funcs_for_maps)
        self._module_method_field_old_ensures = self._build_method_field_old_ensures_map(funcs_for_maps)
        self._module_method_field_param_post_ensures = \
            self._build_method_field_param_post_ensures_map(funcs_for_maps)
        self._module_method_field_param_frame_ensures = \
            self._build_method_field_param_frame_ensures_map(funcs_for_maps)
        # fd-import-boundary: the `\result`-referencing single-cell quantified self-field
        # FRAME (`\forall k != \result. fd_open[k] == \old(fd_open[k])`), opt-in via
        # `#@ propagate_frame`. The map above DROPS `\result`-frames; this one keeps exactly
        # those, so the os fd allocators' single-cell frame survives the import boundary (the
        # "table not full" side-condition the honest no-ENFILE needs). `\result` lowers to the
        # val's `result` keyword at the call site, so no explicit substitution is required.
        self._module_method_result_frame_ensures = \
            self._build_method_result_frame_ensures_map(funcs_for_maps)
        # The pseudo-funcs have empty bodies, so the return-type map derives `unit`
        # for a scalar dependency; override with the type from the declared signature
        # so `self.<dep>(…)` is a `: int` (etc.) call, not `: unit`.
        for pf in self._mixin_dep_pseudo_functions(functions):
            self._module_method_return_types[pf["name"]] = pf["_mixin_ret_whyml"]
        self._build_callee_no_exception_summary(functions)

        sorted_functions, scc_info = sort_functions_by_scc(functions)
        self._emitted_logic_funcs = set()
        self._late_content_ops = []
        for func in sorted_functions:
            out += self._emit_function(func, scc_info)

        if self.check_behavioral_subtyping:
            out += self._emit_subtyping_goals(functions)

        out.append("end")
        self._insert_abstract_val_block(out)
        self._insert_late_content_ops(out)
        self._resolve_deferred_exprir_theory(out)
        return "\n".join(out)

    # ------------------------------------------------------------------
    # parser-primitives-wall-impl-3.md capability (i)
    # ------------------------------------------------------------------
    def _exprir_theory_symbols(self, theory_lines: List[str]) -> Set[str]:
        """Every top-level WhyML name the emit_ir theory DECLARES: type names,
        `with`-group members, constructors, `let (rec) function` / `val` / `lemma`
        / `exception` names, and the inline record field labels. Derived from the
        theory's OWN emitted text (same discipline as
        `_reserved_exprir_symbols`), so it can never drift out of sync."""
        text = "\n".join(theory_lines)
        names: Set[str] = set()
        names.update(re.findall(r"^\s*type\s+(\w+)", text, re.M))
        names.update(re.findall(r"\bwith\s+(\w+)\s*=", text))
        names.update(re.findall(r"\blet\s+(?:rec\s+)?function\s+(\w+)", text))
        names.update(re.findall(r"\bval\s+(\w+)", text))
        names.update(re.findall(r"\blemma\s+(\w+)", text))
        names.update(re.findall(r"\bexception\s+(\w+)", text))
        # Constructors of the sum types (`IrVar`, `ILCons`, `INum`, …): the
        # capitalized identifiers on a `type`/`with` declaration line.
        for line in theory_lines:
            if re.match(r"^\s*(type|with)\s+\w+", line):
                names.update(re.findall(r"\b([A-Z]\w*)\b", line))
        # inline record types declared within the theory (`sharedvar`) — their
        # field labels share the module namespace too.
        for rec_body in re.findall(r"\{([^{}]*)\}", text):
            names.update(re.findall(r"(\w+)\s*:", rec_body))
        names.discard("")
        return names

    def _resolve_deferred_exprir_theory(self, out: List[str]) -> None:
        """Splice the deferred emit_ir theory into its parked slot iff the rest of
        the emitted file references a symbol the theory declares; otherwise drop
        the slot. See the deferral comment in `transpile`. No-op (and no sentinel
        in `out`) whenever the theory was emitted eagerly or not at all."""
        info = getattr(self, "_exprir_deferred", None)
        if not info:
            return
        marker, theory = info
        self._exprir_deferred = None
        try:
            idx = out.index(marker)
        except ValueError:      # pragma: no cover - defensive
            return
        rest = "\n".join(out[idx + 1:])
        names = self._exprir_theory_symbols(theory)
        used = bool(names) and bool(re.search(
            r"\b(?:" + "|".join(re.escape(n) for n in sorted(names)) + r")\b", rest))
        if used:
            out[idx:idx + 1] = theory
        else:
            del out[idx]

    # ------------------------------------------------------------------
    # module-emission.md — OPT-IN axiom isolation via separate Why3 modules
    # ------------------------------------------------------------------
    def _verify_module_groups(self, functions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """{group-name -> [whyml function names]} for every `#@ verify_module <name>`
        group, deterministic. Empty when no function is tagged (→ flat path)."""
        groups: Dict[str, List[str]] = {}
        for f in functions:
            g = f.get("verify_module")
            if g:
                groups.setdefault(g, []).append(whyml_ident(f["name"]))
        return groups

    def _compute_shared_module_maps(self, functions: List[Dict[str, Any]]) -> None:
        """Populate the SHARED cross-function lookup state (return-types, contract-
        propagation ensures maps, no_exception summary, …) from the FULL function set
        — identical to the maps `transpile()` builds at lines ~491-588. These are
        global to the program (a cross-module call still needs the callee's propagated
        contract), so they are computed ONCE here and reused for every emitted module."""
        self._module_func_names = {whyml_ident(func["name"]) for func in functions}
        self._sibling_concrete_methods = {whyml_ident(func["name"]) for func in functions
                                          if func.get("sibling_concrete")}
        self._composed_provider_methods = set(self.ir.get("composed_provider_methods", []))
        self._inductive_preds = (
            {ind["name"] for ind in self.ir.get("inductive_decls", [])}
            | {m["name"] for ind in self.ir.get("inductive_decls", [])
               for m in ind.get("members", [])})
        funcs_for_maps = functions + self._mixin_dep_pseudo_functions(functions)
        self._module_method_return_types = self._build_method_return_type_map(funcs_for_maps)
        self._module_method_param_types = self._build_method_param_types_map(funcs_for_maps)
        # wrong-lowering-to-fix.md §WL-05b: func-name -> {dict/set params modelled as a
        # caller-visible mutable `ref (map ...)` (fixpoint over direct item-mutation +
        # transitive param forwarding). Consulted at call sites (pass the bare ref) and
        # in `_reset_function_state` (ref param type + `writes` frame). Empty for every
        # read-only-collection program -> byte-identical.
        self._func_mutated_collection_params = \
            self._build_func_mutated_collection_params(funcs_for_maps)
        # stmt-list-append-mutation wall (C-bucket): see the parallel setup above.
        self._func_stmt_seq_mut_params = \
            self._build_func_stmt_seq_mut_params(funcs_for_maps)
        self._module_method_formal_params = {
            f["name"]: list(f.get("formal_params", [])) for f in funcs_for_maps}
        self._module_method_param_defaults = {
            f["name"]: dict(f.get("param_defaults", {})) for f in funcs_for_maps}
        self._module_method_param_whyml_types = \
            self._build_method_param_whyml_types_by_name(funcs_for_maps)
        self._module_method_return_annotations = \
            self._build_method_return_annotation_map(funcs_for_maps)
        self._module_string_seq_funcs = {
            f["name"] for f in funcs_for_maps if self._func_returns_string_seq(f)}
        self._module_method_result_ensures = self._build_method_result_ensures_map(funcs_for_maps)
        self._module_method_param_result_ensures = self._build_method_param_result_ensures_map(funcs_for_maps)
        self._module_method_field_result_ensures = self._build_method_field_result_ensures_map(funcs_for_maps)
        self._module_method_field_param_result_ensures = \
            self._build_method_field_param_result_ensures_map(funcs_for_maps)
        self._module_method_writes = self._build_method_writes_map(funcs_for_maps)
        self._module_method_field_old_ensures = self._build_method_field_old_ensures_map(funcs_for_maps)
        self._module_method_field_param_post_ensures = \
            self._build_method_field_param_post_ensures_map(funcs_for_maps)
        self._module_method_field_param_frame_ensures = \
            self._build_method_field_param_frame_ensures_map(funcs_for_maps)
        self._module_method_result_frame_ensures = \
            self._build_method_result_frame_ensures_map(funcs_for_maps)
        for pf in self._mixin_dep_pseudo_functions(functions):
            self._module_method_return_types[pf["name"]] = pf["_mixin_ret_whyml"]
        self._build_callee_no_exception_summary(functions)

    # ------------------------------------------------------------------
    # module-emission.md — per-module emission helpers
    # ------------------------------------------------------------------
    def _emit_prefunctions_infra(self, functions: List[Dict[str, Any]],
                                 type_decls: List[Dict[str, Any]],
                                 all_bodies: List[Any],
                                 module_name: str,
                                 emit_axioms: bool,
                                 axiom_ir: Dict[str, Any]) -> List[str]:
        """Emit the SHARED pre-functions infrastructure (preamble `use`s + helpers +
        predicates + `val function` symbols + record type + class-inv axioms + record
        witness + module globals + inductive decls) under header `module <module_name>`.
        Mirrors `transpile()` lines ~410-489 EXACTLY (so the shape matches the flat
        path), except: (a) the module header name is parameterised, and (b) `#@ proof`
        axioms are emitted ONLY when `emit_axioms` is True and are routed through
        `axiom_ir` (a per-module function-subset IR) so a module sees only its group's
        cited axioms. Does NOT emit `let` functions or the abstract-val block."""
        needs = self._scan_preamble_needs(functions, all_bodies)
        out = self._emit_preamble(needs, module_name)
        out += self._emit_shared_state()
        self._precompute_axiom_logic_funcs(self.ir)
        if self._class_inv_refs_axiom_func(self.ir):
            out += self._emit_uncited_axiom_func_decls()
            out += self._emit_class_inv_axioms(self.ir)
        type_lines, declared_types = self._emit_type_decls(type_decls)
        out += type_lines
        # value-model campaign incr5 (primitive c): declare `Return_<variant>` exceptions HERE —
        # after the synthesized `_union_*` types are in scope — for early-returning Optional[X]
        # walkers. Empty (byte-identical) for modules with none.
        out += self._emit_union_return_exceptions(needs, declared_types)
        out += self._emit_module_const_compound_maps()
        self._inductive_preds = (
            {ind["name"] for ind in self.ir.get("inductive_decls", [])}
            | {m["name"] for ind in self.ir.get("inductive_decls", [])
               for m in ind.get("members", [])})
        self._precompute_axiom_logic_funcs(self.ir)
        if self._inductive_refs_global_or_axiom_func(self.ir):
            if emit_axioms:
                out += self._emit_preamble_axioms(axiom_ir)
            out += self._emit_uncited_axiom_func_decls()
            out += self._emit_module_globals()
            out += self._emit_inductive_decls(self.ir.get("inductive_decls", []))
        else:
            out += self._emit_inductive_decls(self.ir.get("inductive_decls", []))
            if emit_axioms:
                out += self._emit_preamble_axioms(axiom_ir)
            out += self._emit_uncited_axiom_func_decls()
            out += self._emit_module_globals()
        self._emit_opaque_class_aliases(functions, out, declared_types)
        self._declared_types_modular = declared_types
        return out

    def _reset_module_accumulators(self) -> None:
        """Reset the per-module emission accumulators so each emitted Why3 `module`
        gets its OWN abstract-val block / axiom-decl set / class-inv-axiom set (the
        flat path leaves these global)."""
        self._abstract_ops = {}
        self._axiom_emitted_decls = set()
        self._class_inv_axioms_emitted = set()

    def _sig_val_from_let(self, let_lines: List[str]) -> List[str]:
        """Convert an emitted `let <fn> ... = <body>` block into a bodyless interface
        `val <fn> ...` carrying ONLY the contract (requires/ensures/writes), dropping the
        `variant` (illegal on a bodyless `val`) and everything from the `=` onward. This
        is the `<G>Sig` interface declaration the provider's `clone`-refinement proves and
        the consumer module calls — the PROVEN cross-module boundary (no assumed `val`)."""
        out: List[str] = []
        for ln in let_lines:
            stripped = ln.strip()
            if stripped.startswith("let function "):
                out.append(ln.replace("let function ", "val ", 1))
                continue
            if stripped.startswith("let rec "):
                out.append(ln.replace("let rec ", "val ", 1))
                continue
            if stripped.startswith("let "):
                out.append(ln.replace("let ", "val ", 1))
                continue
            if stripped == "=" or stripped.startswith("= "):
                break
            if stripped.startswith("variant"):
                continue  # a bodyless `val` cannot carry a variant
            # requires / ensures / writes / reads / raises / diverges lines pass through
            out.append(ln)
        return out

    def _transpile_modular(self, functions: List[Dict[str, Any]],
                           type_decls: List[Dict[str, Any]]) -> str:
        """module-emission.md — emit the program as SEVERAL top-level Why3 `module`s so
        that each `#@ verify_module <name>` group's cited `#@ proof` axioms are isolated
        from the other groups' goals (resolving the os read+write `field_to_str`
        co-residence OOM that blocks `_dir_lookup`). PARTIAL BUILD — see
        getting-better/<writeup> §"remaining emitter work": the sound MECHANISM
        (Why3 `clone`-refinement, axiom-isolated, narrowing-VC-equivalent) is PROVEN at
        the Why3 level and validated on the real os axiom families
        (getting-better validation artifact /tmp/os_split.mlw → `'refn'vc` Valid +
        non-vacuous), and this directive is wired through the full pipeline + corpus-
        inert, but the multi-module emitter assembly below is NOT yet complete enough to
        pass the full body gate ×2. It is left raising a clear, actionable error rather
        than emitting an unsound/under-verified module split."""
        from module6_whyml.scc import sort_functions_by_scc

        groups = self._verify_module_groups(functions)
        all_bodies = [func["body"] for func in functions]

        # Cross-function contract-propagation maps are GLOBAL to the program (a cross-
        # module call still needs the callee's propagated contract). Compute ONCE.
        self._compute_shared_module_maps(functions)

        # {whyml_fn_name -> group}; consulted by `_handle_dotted_call` to route a
        # cross-module `self.<m>()` through the proven `<G>Sig` interface.
        self._verify_module_of = {}
        for g, names in groups.items():
            for nm in names:
                self._verify_module_of[nm] = g

        # cleared-array item 1: reset the logic-symbol tracking for this module set
        # (call-comprehension lifting). The late-content-op flush (per module) below
        # anchors each deferred content-law val to its using function.
        self._emitted_logic_funcs = set()
        self._late_content_ops = []
        # Partition the SORTED function list (preserve emission order) into the main
        # (untagged) set + one list per group.
        sorted_functions, scc_info = sort_functions_by_scc(functions)
        group_funcs: Dict[str, List[Dict[str, Any]]] = {g: [] for g in groups}
        main_funcs: List[Dict[str, Any]] = []
        for func in sorted_functions:
            wn = whyml_ident(func["name"])
            g = self._verify_module_of.get(wn)
            if g is not None:
                group_funcs[g].append(func)
            else:
                main_funcs.append(func)

        def _emit_funcs(funcs: List[Dict[str, Any]], group: Optional[str]) -> List[str]:
            """Emit the `let` blocks for `funcs`, with `_current_emit_group` set so a
            cross-module `self.<m>()` routes through `<G>Sig`. Returns the lines."""
            # The `val function` axiom-symbols (slot_inode/slot_name/dir_lookup/…) all
            # live in `Shared` and are `use`d by every emitted module, so a contract
            # application of one must bind to that shared logic symbol — NOT an unbound
            # arity-suffixed abstract op. The flat `_precompute_axiom_logic_funcs(ir)`
            # derives these from `ir["functions"]`' `#@ proof` cites; in the split a cited
            # function may live in another module, so precompute from the FULL ir here.
            self._precompute_axiom_logic_funcs(self.ir)
            self._current_emit_group = group
            lines: List[str] = []
            for func in funcs:
                lines += self._emit_function(func, scc_info)
            self._current_emit_group = None
            return lines

        # ============================ Shared ============================
        # The concrete record type + invariants + concrete predicates/functions + the
        # shared `val function` symbols + record-witness/class-inv axioms + globals.
        # A DEFINED record type cannot be clone-substituted, so it MUST live here and be
        # `use`d by every other module. NO `#@ proof` axioms here (routed per-module).
        # Shared emits NO `let` functions, so it registers NO abstract ops (verified:
        # `_emit_prefunctions_infra` with an empty function set leaves `_abstract_ops`
        # empty) — every abstract-op call stub (`subscript_get`, `materialize`, the
        # `_filesystem_sys_*` importer stubs, the `self__*` sibling stubs) is caller-local
        # and is emitted by the module whose functions USE it, in that module's own
        # abstract-val block (no cross-module `use` of these → no duplicate-symbol clash).
        self._shared_op_skip = set()
        self._reset_module_accumulators()
        shared = self._emit_prefunctions_infra(
            functions, type_decls, all_bodies,
            module_name="Shared", emit_axioms=False, axiom_ir={**self.ir, "functions": []})
        shared.append("end")
        self._insert_abstract_val_block(shared)  # no-op: Shared has no abstract ops

        # Capture the axiom-backing logic-symbol DECLARATIONS Shared emitted
        # (`val function slot_inode …`, `predicate uniq …`, `function inode_size …`).
        # Every other module `use Shared`, so it must reference these via the shared
        # symbol — re-declaring them locally would create a DISTINCT symbol, breaking the
        # `clone`-refinement (the body's `dir_lookup` would differ from the interface's).
        # Pre-seeding each subsequent module's `_axiom_emitted_decls` with these strings
        # makes `_emit_preamble_axioms`/`_emit_uncited_axiom_func_decls` skip the decl but
        # still emit the AXIOM (which now constrains the shared symbol).
        self._shared_symbol_decls = self._collect_shared_symbol_decls(shared)

        out_modules: List[List[str]] = [shared]

        # ===================== per-group Sig + provider =====================
        for g in sorted(groups):
            gfuncs = group_funcs[g]
            cited_ir = {**self.ir, "functions": gfuncs}

            # ---- <G>Sig : bodyless contract `val`s (the proven interface) ----
            sig: List[str] = [f"module {g}Sig"]
            sig += self._shared_use_lines()
            self._reset_module_accumulators()
            self._precompute_axiom_logic_funcs(self.ir)
            self._current_emit_group = g
            for func in gfuncs:
                let_block = self._emit_function(func, scc_info)
                sig += self._sig_val_from_let(let_block)
                sig.append("")
            self._current_emit_group = None
            sig.append("end")
            out_modules.append(sig)

            # ---- <G> : shared symbols + group axioms LOCALLY + real let + clone ----
            prov: List[str] = [f"module {g}"]
            prov += self._shared_use_lines()
            self._reset_module_accumulators()
            self._axiom_emitted_decls = set(self._shared_symbol_decls)
            # The group's cited `#@ proof` axioms, emitted LOCALLY (in scope only here).
            # The backing symbol DECLS are suppressed (seeded above) so the axioms
            # constrain the SHARED symbols (`use Shared`), keeping body == interface.
            prov += self._emit_preamble_axioms(cited_ir)
            prov_body = _emit_funcs(gfuncs, g)
            prov += prov_body
            # Trailing clone-refinement: generates `<fn>'refn'vc` proving the real `let`
            # implements the `<G>Sig` contract — the PROVEN boundary (never an assumed val).
            subs = ", ".join(f"val {whyml_ident(f['name'])} = {whyml_ident(f['name'])}"
                             for f in gfuncs)
            prov.append(f"  clone {g}Sig with {subs}")
            prov.append("end")
            self._insert_abstract_val_block(prov)
            out_modules.append(prov)

        # ============================ PyCSL_Program ============================
        # The main module: everything else + the NON-group axioms + `use Shared` +
        # `use <G>Sig` (proven interfaces), with cross-module `self.X()` calls rewritten.
        main_ir = {**self.ir, "functions": main_funcs}
        main: List[str] = ["module PyCSL_Program"]
        main += self._shared_use_lines()
        for g in sorted(groups):
            main.append(f"  use {g}Sig")
        self._reset_module_accumulators()
        self._axiom_emitted_decls = set(self._shared_symbol_decls)
        main += self._emit_preamble_axioms(main_ir)
        main += _emit_funcs(main_funcs, None)
        if self.check_behavioral_subtyping:
            main += self._emit_subtyping_goals(functions)
        main.append("end")
        self._insert_abstract_val_block(main)
        # cleared-array item 1: flush any deferred call-comprehension content-law
        # vals into the main module (their using functions are the untagged set).
        # A call comprehension inside a `#@ verify_module` group is unsupported (the
        # anchor would not be in `main`); the missing decl fails the L3 typecheck
        # loudly — never a false proof.
        self._insert_late_content_ops(main)
        out_modules.append(main)

        return "\n".join("\n".join(m) for m in out_modules)

    def _collect_shared_symbol_decls(self, shared_lines: List[str]) -> Set[str]:
        """Scan the emitted Shared module for axiom-backing logic-symbol declarations and
        return the SET OF RAW `_AXIOM_FUNCTIONS` decl strings whose symbol Shared declares.
        Those raw strings are what `_emit_preamble_axioms`/`_emit_uncited_axiom_func_decls`
        compare against (`if fn_decl not in declared_fns`), so seeding a subsequent
        module's `_axiom_emitted_decls` with them suppresses the duplicate decl while the
        AXIOM (constraining the SHARED symbol) is still emitted. A module that `use Shared`
        must reference the SAME symbol — a local re-declaration would break the
        `clone`-refinement (body `dir_lookup` ≠ interface `dir_lookup`)."""
        def _symbol(stripped: str):
            p = stripped.split()
            if len(p) >= 3 and p[0] == "val" and p[1] == "function":
                return p[2]
            if len(p) >= 2 and p[0] in ("function", "predicate"):
                return p[1]
            return None

        shared_syms: Set[str] = set()
        for ln in shared_lines:
            sym = _symbol(ln.strip())
            if sym:
                shared_syms.add(sym)
        # Map back to the raw registry decl strings (exact match for the skip-check).
        raw: Set[str] = set()
        for fn_decls in self._AXIOM_FUNCTIONS.values():
            for d in fn_decls:
                if _symbol(d.strip()) in shared_syms:
                    raw.add(d)
        return raw

    def _shared_use_lines(self) -> List[str]:
        """The `use` lines every emitted module needs to see the Shared infrastructure
        (the concrete record type, val-functions, predicates, helpers) plus the standard
        Why3 library `use`s. Mirrors the libraries the flat preamble imports."""
        needs = self._scan_preamble_needs(
            self.ir.get("functions", []),
            [f["body"] for f in self.ir.get("functions", [])])
        # The flat preamble `use`s, MINUS the `module PyCSL_Program` header line, plus a
        # `use Shared` so the record type + shared symbols are in scope.
        lib_uses = self._emit_preamble_uses(needs, module_name="__tmp__")[1:]
        return lib_uses + ["  use Shared"]

