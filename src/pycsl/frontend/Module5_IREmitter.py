from __future__ import annotations

from frontend import pure_ast as ast  # consume the same pure-Python tree Module3 builds
import json
from typing import Any, Dict, List, Optional, Set, Tuple
from errors import PyCSLIRError
from ir_schema import IR_VERSION
from frontend.module5.memoization_rt import MemoizationRTMixin
from frontend.module5.construction_synth import ConstructionSynthMixin
from frontend.module_collect import collect_module_constants, collect_module_globals
from frontend.Module2_Parser import (
    CSLNode, ContractWrapper,
    Requires, Ensures, LoopInvariant, LoopVariant,
    BinOp as CSLBinOp, UnaryOp as CSLUnaryOp, Var as CSLVar,
    Number as CSLNumber, Result as CSLResult, Old as CSLOld, Nothing,
    FieldAccess as CSLFieldAccess, FieldSubscript as CSLFieldSubscript,
    GlobalFieldSubscript as CSLGlobalFieldSubscript,
    Forall, Exists, ArrayLength, InGlobals, InScope, SubscriptAccess,
    AssignsRegion, Valid, Separated, At as CSLAt,
    Length2D, Valid2D, FunctionVariant, StringLiteral as CSLStringLiteral,
    CallExpr, IsSorted, ArrayEq, Permutation, Sum, CSLBool, CSLNone, CSLIn, CSLNotIn, CSLSlice, DictView, ForallItems,
    ChainedSubscript,
    GhostArraySetDecl,
    MkTupleExpr, FstExpr, SndExpr, ProjExpr, CtorTest, CtorPayload,
    StrConcatExpr, StrLengthExpr, StrSubExpr,
    GhostCopyExpr, GhostCopyRangeExpr, GhostMakeExpr,
    MapEmptyExpr, MapGetExpr, MapSetExpr, MapEqExpr, HasKeyExpr, MapRemoveExpr,
    SetEmptyExpr, SetAddExpr, SetRemoveExpr, SetMemExpr,
    SetUnionExpr, SetInterExpr, SetDiffExpr, SetCardExpr,
    SetSubsetExpr, SetEqExpr,
    NilExpr, ConsExpr, HdExpr, TlExpr, ListLengthExpr,
    NthExpr, MemExpr, AppendExpr,
    Act, Given, Complete, Disjoint,  # pre-desugar acts, plumbed for the core's _check_acts
)

class PyCSLToJSONEmitter(MemoizationRTMixin, ConstructionSynthMixin, ast.NodeVisitor):
    """Walks the Annotated AST and translates it into a JSON-serializable IR."""

    def __init__(self) -> None:
        # Stamp the IR as a versioned wire format (the front-end contract; the
        # Python front-end is the source_language). Module6 ignores these metadata
        # keys, so emission is unchanged — they exist for the core's version gate
        # and for any consumer of the serialized IR.
        self.program_ir = {
            "ir_version": IR_VERSION,
            "source_language": "python",
            "type_decls": [],
            "functions": [],
        }
        self._current_class: Optional[str] = None
        # scc3.md Phase B: the current function's symbol table, set while building its
        # contracts so `_csl_in` can dispatch `x in S` on the collection's type (a set
        # → key membership, a list → positional `exists`). Empty outside that window.
        self._cur_func_symtab: Dict[str, Any] = {}
        # refactor.md B-final (STEP 1): the surface name of the function whose contracts
        # / body are currently being emitted, so `_csl_proj` can name the context in its
        # \proj-index literal guard (the guard migrated here from Module4 — Module5's
        # ProjExpr emission depends on a literal index). `function 'F'` (matching Module4's
        # `self.current_function_name`); set in `_build_function_ir`, empty otherwise.
        self._cur_func_name: str = ""
        self._fresh_var_counter: int = 0
        self._mutex_invariants_csl: Dict[str, Any] = {}  # mutex → CSLNode
        # typing-engagement ty1 / 26-0000-typing-spec-2: per-function accumulators
        # for synthesized Literal contracts. `_cur_literal_requires` collects
        # `requires` IR exprs synthesized from `x: Literal[v1, ..., vn]` parameter
        # annotations; `_cur_literal_ensures` collects `ensures` IR exprs synthesized
        # from `-> Literal[v1, ..., vn]` return annotations. Both are flushed into
        # `func_ir["contracts"]` by `_build_function_ir` AFTER the user-written
        # `csl_requires`/`csl_ensures` (order within requires/ensures is logically
        # conjunctive and commutative, so this is a rendering detail only).
        self._cur_literal_requires: List[Dict[str, Any]] = []
        self._cur_literal_ensures: List[Dict[str, Any]] = []
        # typing-engagement ty1 / 27-0000-typing-spec-3: the per-module Final
        # registry. Each entry records a Final-annotated name and its allowed
        # writer — the degenerate single-attribute, single-writer form of HAPPY's
        # no-write confinement (F1: module-level Final → no function may write;
        # F2: instance-attribute Final → only the declaring class's __init__ may
        # write). Plumbed into `program_ir["final_registry"]` (omitted when empty,
        # so byte-identical for Final-free modules). Consumed by
        # `core_ir_semantic._check_final` (a static write-site check, NOT a VC).
        self._final_registry: List[Dict[str, Any]] = []
        # refactor.md B-final wedge: the set of module-level shared-variable names
        # (from `csl_shared_decls`). Module5 now builds the function symbol_table
        # itself (see `_build_function_symbol_table`), and — like Module4's
        # `_build_function_scope` — must SKIP shared vars when collecting locals.
        # Populated in `visit_Module` before functions are visited via generic_visit.
        self._shared_var_names: Set[str] = set()
        # typing-engagement ty2 / 31-1700-typing-spec-7: per-name pending
        # overload-stub guarded postconditions. Each `@overload def f(...)...`
        # stub synthesizes `isinstance(p_i, T_i) ==> Q_i` IR clauses (O3); these
        # are collected here and appended to the non-`@overload` implementation's
        # `contracts.ensures` when it is visited (O6 — the single body proves each
        # guarded postcondition). The stub itself is NOT emitted as a function IR
        # node (its body is `...`/`pass` — R1, discarded at runtime). Empty for
        # every overload-free module → byte-identical emission.
        self._pending_overloads: Dict[str, List[Dict[str, Any]]] = {}

        # typing-engagement ty2 / 32-1700-typing-spec-8: Protocol interface registry.
        # `self._protocols[P] = {m1, m2, ...}` records each Protocol class's member
        # names so a `#@ conforms_to P` class can populate `overrides` with
        # `(C__m, P__m)` pairs (P2/P4 per-method contract-refinement VCs). Empty for
        # every Protocol-free module → byte-identical emission.
        self._protocols: Dict[str, set] = {}

    def visit_Module(self, node: ast.Module) -> None:
        """Emit module-level concurrency declarations into the top-level IR."""
        shared_decls = getattr(node, 'csl_shared_decls', [])
        mutex_invs = getattr(node, 'csl_mutex_invariants', {})
        lock_order = getattr(node, 'csl_lock_order', None)

        # refactor.md B-final wedge: record shared-var names so the self-built
        # function symbol_table skips them (mirrors Module4's `self._shared_vars`
        # keys, populated from the same `csl_shared_decls`).
        self._shared_var_names = {d.variable for d in shared_decls}

        # Store CSL nodes so _get_mutex_invariant_ir can look them up later
        self._mutex_invariants_csl = dict(mutex_invs)

        if shared_decls:
            self.program_ir["shared_vars"] = [
                {"name": d.variable, "mutex": d.mutex}
                for d in shared_decls
            ]
        if mutex_invs:
            self.program_ir["mutex_invariants"] = {
                mutex: self._csl_to_ir(expr)
                for mutex, expr in mutex_invs.items()
            }
        if lock_order is not None:
            self.program_ir["lock_order"] = lock_order.order

        # B-final STEP 4: plumb the bare names of `#@ \trusted` functions so the core's
        # `_check_lemma` can reject a plain lemma body that calls a trusted (unverified)
        # fact. Mirrors Module4's `self._trusted_funcs` (which collected `n.name` over
        # every FunctionDef with `csl_trusted`); a lemma body's IR `Call.func` is the same
        # bare name, so matching by bare name reproduces the check. Sorted for determinism.
        trusted_funcs = sorted({
            n.name for n in ast.walk(node)
            if isinstance(n, ast.FunctionDef) and getattr(n, 'csl_trusted', False)})
        if trusted_funcs:
            self.program_ir["trusted_funcs"] = trusted_funcs

        # refactor.md Phase C (C1): emit the module's import list into the IR so
        # multi-file import resolution (pycsl._resolve_imports) becomes a pure
        # IR→IR pass instead of re-walking the Python AST. This MUST reproduce
        # exactly what pycsl._extract_imports yielded — same ast.walk ordering,
        # same per-alias tuple shape (local, original, module, level, is_module)
        # — so the set/order of injected dependency functions is byte-identical.
        # Additive field: Module 6 ignores it (emission unchanged for any driver).
        imports_ir: List[List[Any]] = []
        for n in ast.walk(node):
            if isinstance(n, ast.ImportFrom) and n.module:
                for alias in n.names:
                    if alias.name == '*':
                        imports_ir.append(["*", "*", n.module, n.level or 0, False])
                        continue
                    local = alias.asname if alias.asname else alias.name
                    imports_ir.append([local, alias.name, n.module, n.level or 0, False])
            elif isinstance(n, ast.Import):
                for alias in n.names:
                    local = alias.asname if alias.asname else alias.name
                    imports_ir.append([local, alias.name, alias.name, 0, True])
        if imports_ir:
            self.program_ir["imports"] = imports_ir

        # module-constants-plan: module-level int constants (`K_IHDR = 0`) →
        # resolved to their literal in Module 6 (body and contract).
        module_consts = collect_module_constants(node)
        if module_consts:
            self.program_ir["module_constants"] = module_consts

        # inline.md Phase 1: module-level global object instances `g = C(...)`. Modeled
        # in Module 6 as a Why3 mutable-record global `let g : c = <ctor>`; the ctor
        # `value` reuses the record-construction lowering (`_call_record_constructor`).
        _class_names = {c.name for c in node.body if isinstance(c, ast.ClassDef)}
        # inline.md: also include names imported via `from X import Y` — they
        # may be classes defined in another module whose type_decl will be
        # injected later by _resolve_imported_classes.  collect_module_globals
        # filters out non-class uses anyway (must be a Call with that name).
        for stmt in node.body:
            if isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    _class_names.add(alias.asname or alias.name)
        module_globals = collect_module_globals(node, _class_names)
        if module_globals:
            self.program_ir["module_globals"] = [
                {"name": nm, "class": call.func.id, "value": self._py_expr_to_ir(call)}
                for nm, call in module_globals.items()
            ]

        # Plumb module-level HAPPY for the core's cross-method validation
        # (core_ir_semantic._check_happy; refactor.md AST-only #3). The Python-specific
        # facts are resolved in the front-end (where the AST + SHORT method names live —
        # the IR flattens method names to Class__method): the declared properties, the
        # module's method names, and which methods contain a dynamic `exec` (a worst-case
        # mutator). The core collects written fields from the IR and does the logic.
        happy_props = getattr(node, 'csl_happy_properties', []) or []
        if happy_props:
            method_names: List[str] = []
            exec_methods: List[str] = []
            for _n in ast.walk(node):
                if isinstance(_n, ast.FunctionDef):
                    method_names.append(_n.name)
                    for _sub in ast.walk(_n):
                        if (isinstance(_sub, ast.Call)
                                and isinstance(getattr(_sub, "func", None), ast.Name)
                                and _sub.func.id == "exec"):
                            exec_methods.append(_n.name)
                            break
            self.program_ir["happy"] = {
                # H-I1 read-confinement (context=="reading") properties are fully realised
                # as injected per-read `#@ check`s by Module3 (with their own aliasing /
                # trust-boundary / exec well-formedness checks there), so they are NOT
                # emitted into this blob — keeping the IR byte-identical for write-confinement
                # files and avoiding `_check_happy`'s write-oriented "inert field" warning.
                "properties": [
                    {"name": hp.name, "field": hp.field,
                     "protects": hp.protects, "except_set": list(hp.except_set)}
                    for hp in happy_props
                    if getattr(hp, "context", "writing")
                       not in ("reading", "postcond", "precond", "total", "noninterference")],
                "method_names": method_names,
                "exec_methods": exec_methods,
            }

        # collections-plan: synthesise record type_decls for module-level
        # `Name = namedtuple(...)` BEFORE visiting functions, so a `Name(...)`
        # construction resolves against `_record_types`.
        self._synthesize_namedtuple_records(node)
        # typing-engagement ty2 / 29-1700-typing-spec-5: synthesise record
        # type_decls for the functional form `Name = TypedDict("Name", {...})`.
        # Best-effort literal-only; a non-literal fields dict falls through
        # unchanged (byte-identical fallback).
        self._synthesize_typeddict_functional(node)
        # typing-engagement ty2 / 30-1700-typing-spec-6: synthesise record
        # type_decls for the functional form `Name = NamedTuple("Name", [...])`.
        # Best-effort literal-only; a non-literal fields list falls through
        # unchanged (byte-identical fallback).
        self._synthesize_namedtuple_functional(node)

        # sum-types: `#@ datatype Name = C1 | C2(int) | …` → a variant type_decl, and a
        # constructor registry so a `C1` / `C2(x)` value and a `case C1()` pattern resolve.
        for dt in getattr(node, 'csl_datatypes', []):
            self.program_ir["type_decls"].append({
                "kind": "variant", "name": dt.name,
                # A5d: type parameters of a parametric datatype (`Option[T]`).
                "type_params": list(getattr(dt, "type_params", None) or []),
                "constructors": [{"name": c, "arity": len(tys), "payload": tys}
                                 for (c, tys) in dt.variants],
            })
            for (c, tys) in dt.variants:
                self.program_ir.setdefault("constructors", {})[c] = {
                    "type": dt.name, "arity": len(tys)}

        # inductive.md: `#@ inductive p(params): rule …` → a logic-level inductive
        # predicate. Each rule's Horn-clause body is an ordinary contract expr lowered
        # by Module 6; the IR carries name/signature/[(rule_name, clause_ir)].
        for ind in getattr(node, 'csl_inductives', []):
            self.program_ir.setdefault("inductive_decls", []).append({
                "name": ind.name,
                "signature": ind.signature,
                "rules": [(rname, self._csl_to_ir(rbody))
                          for (rname, rbody) in (ind.rules or [])],
                # inductive.md P2: mutually-inductive `with` group members.
                "members": [
                    {"name": mname, "signature": msig,
                     "rules": [(rn, self._csl_to_ir(rb)) for (rn, rb) in mrules]}
                    for (mname, msig, mrules) in (getattr(ind, 'members', None) or [])
                ],
            })

        # typing-engagement ty1 / 27-0000-typing-spec-3: collect the per-module
        # Final registry (F1 module-level + F2 instance-attribute declarations)
        # BEFORE generic_visit so the class walk sees the resolved class names.
        # Plumbed as `program_ir["final_registry"]` (omitted when empty →
        # byte-identical for Final-free modules). Consumed by the static
        # write-policy check `core_ir_semantic._check_final` (NOT a VC).
        self._collect_final_registry(node)
        if self._final_registry:
            self.program_ir["final_registry"] = list(self._final_registry)

        # typing-engagement ty3 / 33-1700-typing-spec-9: collect the legacy
        # `T = TypeVar("T", bound=B)` / `T = TypeVar("T")` module-level calls so a
        # `class C(Generic[T])` (PEP 484 spelling) can recover the bound from
        # `_collect_type_params`. Omitted when no TypeVar calls exist →
        # byte-identical for non-generic modules (additive IR v1.4 field).
        typevar_registry = self._collect_typevar_registry(node)
        if typevar_registry:
            self.program_ir["typevar_registry"] = typevar_registry

        self.generic_visit(node)

    def _get_mutex_invariant_ir(self, mutex: str) -> Optional[Dict[str, Any]]:
        """Return the IR form of the mutex invariant, or None if not declared."""
        csl_node = self._mutex_invariants_csl.get(mutex)
        if csl_node is None:
            return None
        return self._csl_to_ir(csl_node)

    def _fresh_var(self, prefix: str = "_mem") -> str:
        name = f"{prefix}_{self._fresh_var_counter}"
        self._fresh_var_counter += 1
        return name

    # --- 1. PyCSL Contract Serialization ---

    # Dispatch table: CSL node type → handler method name
    _CSL_HANDLERS: Dict[type, str] = {
        CSLBinOp:         "_csl_binop",
        CSLUnaryOp:       "_csl_unaryop",
        CSLFieldAccess:   "_csl_field_access",
        CSLFieldSubscript: "_csl_field_subscript",
        CSLGlobalFieldSubscript: "_csl_global_field_subscript",
        CSLVar:           "_csl_var",
        CSLNumber:        "_csl_number",
        CSLStringLiteral: "_csl_string",
        CSLBool:          "_csl_bool",
        CSLNone:          "_csl_none",
        CSLResult:        "_csl_result",
        CSLOld:           "_csl_old",
        Nothing:          "_csl_nothing",
        Forall:           "_csl_forall",
        ForallItems:      "_csl_forall_items",
        Exists:           "_csl_exists",
        ArrayLength:      "_csl_array_length",
        InGlobals:        "_csl_in_globals",
        InScope:          "_csl_in_scope",
        SubscriptAccess:  "_csl_subscript",
        AssignsRegion:    "_csl_assigns_region",
        Valid:            "_csl_valid",
        Separated:        "_csl_separated",
        CSLAt:            "_csl_at",
        Length2D:         "_csl_length2d",
        Valid2D:          "_csl_valid2d",
        ContractWrapper:  "_csl_contract_wrapper",
        Requires:        "_csl_contract_wrapper",
        Ensures:         "_csl_contract_wrapper",
        LoopInvariant:   "_csl_contract_wrapper",
        LoopVariant:     "_csl_contract_wrapper",
        FunctionVariant:  "_csl_function_variant",
        CallExpr:         "_csl_call_expr",
        IsSorted:         "_csl_is_sorted",
        ArrayEq:          "_csl_array_eq",
        Permutation:      "_csl_permutation",
        Sum:              "_csl_sum",
        CSLIn:            "_csl_in",
        CSLNotIn:         "_csl_not_in",
        CSLSlice:         "_csl_slice",
        ChainedSubscript: "_csl_chained_subscript",
        # Ghost expression nodes
        MkTupleExpr:      "_csl_mktuple",
        FstExpr:          "_csl_fst",
        SndExpr:          "_csl_snd",
        ProjExpr:         "_csl_proj",
        CtorTest:         "_csl_ctor_test",
        CtorPayload:      "_csl_ctor_payload",
        StrConcatExpr:    "_csl_strconcat",
        StrLengthExpr:    "_csl_str_length",
        StrSubExpr:       "_csl_str_sub",
        GhostCopyExpr:      "_csl_ghost_copy",
        GhostCopyRangeExpr: "_csl_ghost_copy_range",
        GhostMakeExpr:      "_csl_ghost_make",
        MapEmptyExpr:     "_csl_map_empty",
        MapGetExpr:       "_csl_map_get",
        MapSetExpr:       "_csl_map_set",
        MapEqExpr:        "_csl_map_eq",
        HasKeyExpr:       "_csl_has_key",
        MapRemoveExpr:    "_csl_map_remove",
        SetEmptyExpr:     "_csl_set_empty",
        SetAddExpr:       "_csl_set_add",
        SetRemoveExpr:    "_csl_set_remove",
        SetMemExpr:       "_csl_set_mem",
        SetUnionExpr:     "_csl_set_union",
        SetInterExpr:     "_csl_set_inter",
        SetDiffExpr:      "_csl_set_diff",
        SetCardExpr:      "_csl_set_card",
        SetSubsetExpr:    "_csl_set_subset",
        SetEqExpr:        "_csl_set_eq",
        NilExpr:          "_csl_nil",
        ConsExpr:         "_csl_cons",
        HdExpr:           "_csl_hd",
        TlExpr:           "_csl_tl",
        ListLengthExpr:   "_csl_list_length",
        NthExpr:          "_csl_nth",
        MemExpr:          "_csl_mem",
        AppendExpr:       "_csl_append",
    }

    def _csl_to_ir(self, node: CSLNode) -> Dict[str, Any]:
        """Recursively translates PyCSL nodes into IR dictionaries."""
        handler_name = self._CSL_HANDLERS.get(type(node))
        if handler_name is None:
            raise PyCSLIRError(f"Unsupported CSL node: {type(node).__name__}", stage="ir-emit")
        return getattr(self, handler_name)(node)

    def _csl_binop(self, node: CSLBinOp) -> Dict[str, Any]:
        return {"type": "BinOp", "op": node.op,
                "left": self._csl_to_ir(node.left), "right": self._csl_to_ir(node.right)}

    def _csl_unaryop(self, node: CSLUnaryOp) -> Dict[str, Any]:
        return {"type": "UnaryOp", "op": node.op, "expr": self._csl_to_ir(node.expr)}

    def _csl_field_access(self, node: CSLFieldAccess) -> Dict[str, Any]:
        # no-more-int-2 Track 3: `self.f` is a FieldGet; `p.f` on a record-typed param is an
        # Attribute (routed through _handle_attribute_expr, which reads a record param directly).
        # 07-0903 W2: `\result.<field>` — field access on a record-returning function's
        # result. Carry a Result receiver so Module6 emits `result.<field_label>`.
        if node.object == "\\result":
            return {"type": "Attribute",
                    "object": {"type": "Result"}, "attr": node.field}
        if node.object != "self":
            return {"type": "Attribute",
                    "object": {"type": "Var", "name": node.object}, "attr": node.field}
        return {"type": "FieldGet", "object": node.object, "field": node.field}

    def _csl_field_subscript(self, node: CSLFieldSubscript) -> Dict[str, Any]:
        # `self.<field>[i]` → Subscript of a FieldGet, reusing the existing
        # hoare subscript-of-field lowering (module6 `_handle_subscript`).
        return {"type": "Subscript",
                "value": {"type": "FieldGet", "object": "self", "field": node.field},
                "index": self._csl_to_ir(node.index)}

    def _csl_global_field_subscript(self, node: CSLGlobalFieldSubscript) -> Dict[str, Any]:
        # spec-15 / gap-15 Wall B: `<global>.<field>[expr]` → Subscript of an Attribute whose
        # receiver is the module-global Var — the SAME Attribute shape `_csl_field_access` emits
        # for a non-`self` receiver (line ~338-340). Module6 resolves it via the existing gap-10
        # global-field projection + the spec-context `Array.get` branch (no Module6 change).
        return {"type": "Subscript",
                "value": {"type": "Attribute",
                          "object": {"type": "Var", "name": node.obj},
                          "attr": node.field},
                "index": self._csl_to_ir(node.index)}

    def _csl_var(self, node: CSLVar) -> Dict[str, Any]:
        return {"type": "Var", "name": node.name}

    def _csl_number(self, node: CSLNumber) -> Dict[str, Any]:
        return {"type": "Number", "value": node.value}

    def _csl_string(self, node: CSLStringLiteral) -> Dict[str, Any]:
        return {"type": "String", "value": node.value}

    def _csl_bool(self, node: CSLBool) -> Dict[str, Any]:
        return {"type": "Bool", "value": node.value}

    def _csl_none(self, node: CSLNone) -> Dict[str, Any]:
        return {"type": "None"}

    def _csl_result(self, node: CSLResult) -> Dict[str, Any]:
        return {"type": "Result"}

    def _csl_old(self, node: CSLOld) -> Dict[str, Any]:
        # Old(FieldAccess) → OldField (flat node)
        if isinstance(node.expr, CSLFieldAccess):
            return {"type": "OldField", "object": node.expr.object, "field": node.expr.field}
        return {"type": "Old", "expr": self._csl_to_ir(node.expr)}

    def _csl_nothing(self, node: Nothing) -> Dict[str, Any]:
        return {"type": "Nothing"}

    def _csl_forall(self, node: Forall) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Forall", "var": node.var, "body": self._csl_to_ir(node.body)}
        # quantification.md: carry the typed/bounded binder only when present, so a
        # legacy `binder_type=None` quantifier yields a byte-identical IR dict.
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    def _csl_forall_items(self, node: ForallItems) -> Dict[str, Any]:
        # 07-1311 Q3: two-binder dict-items quantifier; Module6 lowers to a `match`.
        return {"type": "ForallItems", "key": node.key, "val": node.val,
                "map": node.coll, "body": self._csl_to_ir(node.body)}

    def _csl_exists(self, node: Exists) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": "Exists", "var": node.var, "body": self._csl_to_ir(node.body)}
        if getattr(node, "binder_type", None) is not None:
            d["binder_type"] = node.binder_type
        if getattr(node, "domain", None) is not None:
            d["domain"] = self._csl_to_ir(node.domain)
        return d

    def _csl_array_length(self, node: ArrayLength) -> Dict[str, Any]:
        return {"type": "ArrayLen", "var": node.var}

    def _csl_in_globals(self, node: InGlobals) -> Dict[str, Any]:
        return {"type": "InGlobals", "name": node.name}   # 07-1839 P2

    def _csl_in_scope(self, node: InScope) -> Dict[str, Any]:
        return {"type": "InScope", "name": node.name}     # 07-1839 P3

    def _csl_subscript(self, node: SubscriptAccess) -> Dict[str, Any]:
        if node.array == "\\result":
            return {"type": "Subscript",
                    "value": {"type": "Result"},
                    "index": self._csl_to_ir(node.index)}
        return {"type": "Subscript",
                "value": {"type": "Var", "name": node.array},
                "index": self._csl_to_ir(node.index)}

    def _csl_chained_subscript(self, node: ChainedSubscript) -> Dict[str, Any]:
        inner = {"type": "Subscript",
                 "value": {"type": "Var", "name": node.array},
                 "index": self._csl_to_ir(node.index1)}
        return {"type": "Subscript",
                "value": inner,
                "index": self._csl_to_ir(node.index2)}

    def _csl_assigns_region(self, node: AssignsRegion) -> Dict[str, Any]:
        return {"type": "AssignsRegion", "base": node.base,
                "low": self._csl_to_ir(node.low), "high": self._csl_to_ir(node.high)}

    def _csl_valid(self, node: Valid) -> Dict[str, Any]:
        return {"type": "Valid", "base": node.base, "length": self._csl_to_ir(node.length)}

    def _csl_separated(self, node: Separated) -> Dict[str, Any]:
        return {"type": "Separated", "base1": node.base1,
                "len1": self._csl_to_ir(node.length1),
                "base2": node.base2, "len2": self._csl_to_ir(node.length2)}

    def _csl_at(self, node: CSLAt) -> Dict[str, Any]:
        return {"type": "At", "expr": self._csl_to_ir(node.expr), "label": node.label}

    def _csl_length2d(self, node: Length2D) -> Dict[str, Any]:
        return {"type": "Length2D", "base": node.base,
                "rows": self._csl_to_ir(node.rows), "cols": self._csl_to_ir(node.cols)}

    def _csl_valid2d(self, node: Valid2D) -> Dict[str, Any]:
        return {"type": "Valid2D", "base": node.base,
                "row": self._csl_to_ir(node.row), "col": self._csl_to_ir(node.col)}

    def _csl_contract_wrapper(self, node: ContractWrapper) -> Dict[str, Any]:
        return self._csl_to_ir(node.expr)

    def _csl_function_variant(self, node: FunctionVariant) -> Dict[str, Any]:
        ir: Dict[str, Any] = {"expr": self._csl_to_ir(node.expr)}
        if node.ordering:
            ir["ordering"] = node.ordering
        return ir

    def _csl_call_expr(self, node: CallExpr) -> Dict[str, Any]:
        return {"type": "Call", "func": node.func,
                "args": [self._csl_to_ir(a) for a in node.args]}

    def _csl_is_sorted(self, node: IsSorted) -> Dict[str, Any]:
        return {"type": "IsSorted", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_array_eq(self, node: ArrayEq) -> Dict[str, Any]:
        return {"type": "ArrayEq",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_permutation(self, node: Permutation) -> Dict[str, Any]:
        return {"type": "Permutation",
                "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_sum(self, node: Sum) -> Dict[str, Any]:
        return {"type": "Sum", "base": node.base,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_in(self, node: CSLIn) -> Dict[str, Any]:
        # scc3.md Phase B: a SET/dict collection has no positional order — `x in S` is
        # KEY membership, not a sequence search. Emit a raw `in` BinOp so Module 6's
        # `_emit_membership` lowers it to the clean `Map.get S x` test (e-matching-
        # friendly, no `Array.length` on a map). The collection name is read straight
        # off the CSL node (not via `_csl_to_ir`) so the list path below keeps its exact
        # `_fresh_var` allocation order → byte-identical. Lists/arrays / unknown types
        # fall through to the positional `exists`.
        # 07-1311 Q1.2: `x in range([lo,] hi)` is a direct integer-interval bound, NOT a
        # positional array search — desugar to `lo <= x and x < hi` (no `Array.length`).
        if isinstance(node.collection, CallExpr) and node.collection.func == "range":
            rargs = node.collection.args
            elt_ir = self._csl_to_ir(node.element)
            if len(rargs) == 1:
                lo_ir = {"type": "Number", "value": 0}
                hi_ir = self._csl_to_ir(rargs[0])
            else:
                lo_ir = self._csl_to_ir(rargs[0])
                hi_ir = self._csl_to_ir(rargs[1])
            return {"type": "BinOp", "op": "and",
                    "left": {"type": "BinOp", "op": "<=", "left": lo_ir, "right": elt_ir},
                    "right": {"type": "BinOp", "op": "<", "left": elt_ir, "right": hi_ir}}
        # 07-1311 Q3: dict views `d.keys()` / `d.values()` (`.items()` is the separate
        # two-binder form). `k in d.keys()` is key presence (≡ bare `k in d`); `v in
        # d.values()` is "v is stored under some key" — `exists _k. Map.get d _k = Some v`.
        if isinstance(node.collection, DictView):
            dv = node.collection
            elt_ir = self._csl_to_ir(node.element)
            coll_var = {"type": "Var", "name": dv.coll}
            if dv.kind == "keys":
                return {"type": "BinOp", "op": "in",
                        "left": elt_ir, "right": coll_var}
            if dv.kind == "values":
                kv = self._fresh_var("_dk")
                return {"type": "Exists", "var": kv,
                        "body": {"type": "MapValueIs",
                                 "map": dv.coll,
                                 "key": {"type": "Var", "name": kv},
                                 "value": elt_ir}}
            raise PyCSLIRError(
                f"`\\forall x in {dv.coll}.items()` (two-binder) is a 07-1311 follow-on; "
                f"use `.keys()`/`.values()` or the `\\forall k in {dv.coll};` key form")
        _coll_nm = getattr(node.collection, "name", None)
        # 07-0647-spec R10/S2.1: a `str` collection is NOT an array — `x in s` on a
        # string is substring containment, handled by Module6's `str_contains_op` (which
        # uses `string.String` and imports it). Desugaring it to the positional array
        # `exists … Array.length …` would use the wrong theory and leave `Array.length`
        # unbound. Defer to Module6 (as set/dict already do) by keeping the `in` BinOp.
        if _coll_nm is not None and self._cur_func_symtab.get(_coll_nm) in (
                "set", "dict", "frozenset", "str"):
            return {"type": "BinOp", "op": "in",
                    "left": self._csl_to_ir(node.element),
                    "right": self._csl_to_ir(node.collection)}
        # x in arr → ∃ v. 0 ≤ v ∧ v < length(arr) ∧ arr[v] == x
        mem_var = self._fresh_var("_mem")
        elt_ir = self._csl_to_ir(node.element)
        coll_ir = self._csl_to_ir(node.collection)
        coll_name = coll_ir.get("name", "_coll")
        return {
            "type": "Exists", "var": mem_var,
            "body": {"type": "BinOp", "op": "and",
                "left": {"type": "BinOp", "op": "and",
                    "left": {"type": "BinOp", "op": ">=",
                        "left": {"type": "Var", "name": mem_var},
                        "right": {"type": "Number", "value": 0}},
                    "right": {"type": "BinOp", "op": "<",
                        "left": {"type": "Var", "name": mem_var},
                        "right": {"type": "ArrayLen", "var": coll_name}}},
                "right": {"type": "BinOp", "op": "==",
                    "left": {"type": "Subscript",
                        "value": {"type": "Var", "name": coll_name},
                        "index": {"type": "Var", "name": mem_var}},
                    "right": elt_ir}}
        }

    def _csl_not_in(self, node: CSLNotIn) -> Dict[str, Any]:
        # x not in arr → ¬(x in arr)
        in_ir = self._csl_to_ir(CSLIn(node.element, node.collection))
        return {"type": "UnaryOp", "op": "not", "expr": in_ir}

    def _csl_slice(self, node: CSLSlice) -> Dict[str, Any]:
        return {"type": "SliceAccess",
                "value": {"type": "Var", "name": node.collection},
                "slice": {"type": "Slice",
                          "lower": self._csl_to_ir(node.low),
                          "upper": self._csl_to_ir(node.high),
                          "step": None}}

    # --- Ghost expression IR handlers ---

    def _csl_mktuple(self, node: MkTupleExpr) -> Dict[str, Any]:
        return {"type": "MkTuple", "elts": [self._csl_to_ir(e) for e in node.elts]}

    def _csl_fst(self, node: FstExpr) -> Dict[str, Any]:
        return {"type": "FstExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    def _csl_snd(self, node: SndExpr) -> Dict[str, Any]:
        return {"type": "SndExpr", "tuple": self._csl_to_ir(node.tuple_expr)}

    def _csl_proj(self, node: ProjExpr) -> Dict[str, Any]:
        # STEP 1 (B-final): \proj index-literal guard, migrated from Module4's
        # `_validate_proj_indices`. ProjExpr emission below reads `node.index.value`,
        # which only exists on a Number literal, so a dynamic index must be rejected here
        # BEFORE `int(...)` crashes. Module4 had the exact surface context (function /
        # while loop at line N / for loop at line N / ghost 'g'); Module5's `_csl_proj`
        # has only the enclosing function, so the context is `function 'F'` for every
        # surface (the affected negative drivers — 0302/0676/0677/0693 — were updated to
        # match; the error still FIRES for each).
        if not isinstance(node.index, CSLNumber):
            from errors import PyCSLSemanticError
            raise PyCSLSemanticError(
                f"\\proj index must be an integer literal in {self._cur_func_name}. "
                "Dynamic projection is not supported."
            )
        return {"type": "ProjExpr", "tuple": self._csl_to_ir(node.tuple_expr),
                "index": int(node.index.value)}

    def _csl_ctor_test(self, node: CtorTest) -> Dict[str, Any]:
        return {"type": "CtorTest", "var": node.var, "ctor": node.ctor}

    def _csl_ctor_payload(self, node: CtorPayload) -> Dict[str, Any]:
        return {"type": "CtorPayload", "var": node.var, "ctor": node.ctor,
                "index": getattr(node, "index", 0)}

    def _csl_strconcat(self, node: StrConcatExpr) -> Dict[str, Any]:
        return {"type": "StrConcat", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_str_length(self, node: StrLengthExpr) -> Dict[str, Any]:
        return {"type": "StrLength", "string": self._csl_to_ir(node.string)}

    def _csl_str_sub(self, node: StrSubExpr) -> Dict[str, Any]:
        return {"type": "StrSub", "string": self._csl_to_ir(node.string),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_ghost_copy(self, node: GhostCopyExpr) -> Dict[str, Any]:
        return {"type": "GhostCopy", "arr": node.arr}

    def _csl_ghost_copy_range(self, node: GhostCopyRangeExpr) -> Dict[str, Any]:
        return {"type": "GhostCopyRange", "arr": node.arr,
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_ghost_make(self, node: GhostMakeExpr) -> Dict[str, Any]:
        return {"type": "GhostMake", "size": self._csl_to_ir(node.size),
                "default": self._csl_to_ir(node.default)}

    def _csl_map_empty(self, node: MapEmptyExpr) -> Dict[str, Any]:
        return {"type": "MapEmpty"}

    def _csl_map_get(self, node: MapGetExpr) -> Dict[str, Any]:
        return {"type": "MapGet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_map_set(self, node: MapSetExpr) -> Dict[str, Any]:
        return {"type": "MapSet", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key), "value": self._csl_to_ir(node.value)}

    def _csl_map_eq(self, node: MapEqExpr) -> Dict[str, Any]:
        return {"type": "MapEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_has_key(self, node: HasKeyExpr) -> Dict[str, Any]:
        return {"type": "HasKey", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_map_remove(self, node: MapRemoveExpr) -> Dict[str, Any]:
        return {"type": "MapRemove", "dict": self._csl_to_ir(node.dict_expr),
                "key": self._csl_to_ir(node.key)}

    def _csl_set_empty(self, node: SetEmptyExpr) -> Dict[str, Any]:
        return {"type": "SetEmpty"}

    def _csl_set_add(self, node: SetAddExpr) -> Dict[str, Any]:
        return {"type": "SetAdd", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    def _csl_set_remove(self, node: SetRemoveExpr) -> Dict[str, Any]:
        return {"type": "SetRemove", "set": self._csl_to_ir(node.set_expr),
                "elem": self._csl_to_ir(node.elem)}

    def _csl_set_mem(self, node: SetMemExpr) -> Dict[str, Any]:
        return {"type": "SetMem", "elem": self._csl_to_ir(node.elem),
                "set": self._csl_to_ir(node.set_expr)}

    def _csl_set_union(self, node: SetUnionExpr) -> Dict[str, Any]:
        return {"type": "SetUnion", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_inter(self, node: SetInterExpr) -> Dict[str, Any]:
        return {"type": "SetInter", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_diff(self, node: SetDiffExpr) -> Dict[str, Any]:
        return {"type": "SetDiff", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_card(self, node: SetCardExpr) -> Dict[str, Any]:
        return {"type": "SetCard", "set": self._csl_to_ir(node.set_expr),
                "lo": self._csl_to_ir(node.lo), "hi": self._csl_to_ir(node.hi)}

    def _csl_set_subset(self, node: SetSubsetExpr) -> Dict[str, Any]:
        return {"type": "SetSubset", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_set_eq(self, node: SetEqExpr) -> Dict[str, Any]:
        return {"type": "SetEq", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_nil(self, node: NilExpr) -> Dict[str, Any]:
        return {"type": "Nil"}

    def _csl_cons(self, node: ConsExpr) -> Dict[str, Any]:
        return {"type": "Cons", "head": self._csl_to_ir(node.head),
                "tail": self._csl_to_ir(node.tail)}

    def _csl_hd(self, node: HdExpr) -> Dict[str, Any]:
        return {"type": "Hd", "list": self._csl_to_ir(node.list_expr)}

    def _csl_tl(self, node: TlExpr) -> Dict[str, Any]:
        return {"type": "Tl", "list": self._csl_to_ir(node.list_expr)}

    def _csl_list_length(self, node: ListLengthExpr) -> Dict[str, Any]:
        return {"type": "ListLength", "list": self._csl_to_ir(node.list_expr)}

    def _csl_nth(self, node: NthExpr) -> Dict[str, Any]:
        return {"type": "Nth", "list": self._csl_to_ir(node.list_expr),
                "index": self._csl_to_ir(node.index)}

    def _csl_mem(self, node: MemExpr) -> Dict[str, Any]:
        return {"type": "Mem", "elem": self._csl_to_ir(node.elem),
                "list": self._csl_to_ir(node.list_expr)}

    def _csl_append(self, node: AppendExpr) -> Dict[str, Any]:
        return {"type": "Append", "left": self._csl_to_ir(node.left),
                "right": self._csl_to_ir(node.right)}

    def _csl_list_to_ir(self, csl_list: List[CSLNode]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for c in csl_list:
            d = self._csl_to_ir(c)
            # Module3 tags act-desugared ensures with `act_name` for attribution;
            # carry it into the IR so Module6 can emit a `(* act NAME *)` comment.
            an = getattr(c, "act_name", None)
            if an is not None and isinstance(d, dict):
                d["act_name"] = an
            out.append(d)
        return out

    def _comprehension_generators_to_ir(self, generators: List[ast.comprehension]) -> List[Dict[str, Any]]:
        """Translate Python comprehension generators to IR."""
        return [
            {
                "target": gen.target.id if isinstance(gen.target, ast.Name) else "_comp_var",
                "iter": self._py_expr_to_ir(gen.iter),
                "ifs": [self._py_expr_to_ir(if_) for if_ in gen.ifs],
            }
            for gen in generators
        ]

    # --- 2. Python AST Serialization (Restricted Subset) ---
    def _py_op_to_str(self, op: ast.operator | ast.cmpop | ast.unaryop) -> str:
        return self._PY_OP_MAP.get(type(op), "?")

    # Dispatch table: Python AST expression type → handler method name
    _PY_EXPR_HANDLERS: Dict[type, str] = {
        ast.Name:       "_py_expr_name",
        ast.Constant:   "_py_expr_constant",
        ast.UnaryOp:    "_py_expr_unaryop",
        ast.BinOp:      "_py_expr_binop",
        ast.Compare:    "_py_expr_compare",
        ast.BoolOp:     "_py_expr_boolop",
        ast.Call:       "_py_expr_call",
        ast.Tuple:      "_py_expr_tuple",
        ast.Subscript:  "_py_expr_subscript",
        ast.List:       "_py_expr_list",
        ast.Attribute:  "_py_expr_attribute",
        ast.Dict:       "_py_expr_dict",
        ast.Set:        "_py_expr_set",
        ast.ListComp:   "_py_expr_listcomp",
        ast.SetComp:    "_py_expr_setcomp",
        ast.DictComp:   "_py_expr_dictcomp",
        ast.JoinedStr:  "_py_expr_fstring",
        ast.IfExp:      "_py_expr_ifexp",
        ast.Starred:    "_py_expr_starred",
        ast.NamedExpr:  "_py_expr_walrus",
        ast.Lambda:     "_py_expr_lambda",
        ast.Slice:      "_py_expr_slice",
    }

    def _py_expr_to_ir(self, expr: ast.expr) -> Dict[str, Any]:
        """Translates Python expressions into IR dictionaries."""
        handler_name = self._PY_EXPR_HANDLERS.get(type(expr))
        if handler_name is not None:
            return getattr(self, handler_name)(expr)
        return {"type": "UnknownPyExpr"}

    def _py_expr_name(self, expr: ast.Name) -> Dict[str, Any]:
        if expr.id in ("Ellipsis",):
            return {"type": "Number", "value": 0}
        if expr.id == "None":
            return {"type": "None"}
        return {"type": "Var", "name": expr.id}

    def _py_expr_constant(self, expr: ast.Constant) -> Dict[str, Any]:
        if expr.value is None:
            return {"type": "None"}
        if isinstance(expr.value, bool):
            return {"type": "Bool", "value": expr.value}
        if isinstance(expr.value, str):
            return {"type": "String", "value": expr.value}
        if isinstance(expr.value, bytes):
            # Per missing-bytes-struct-feature.md Phase 1: bytes
            # literals lower to ArrayLit of int (one element per
            # byte, 0..255). This lets the existing array-int
            # emission path absorb them, and b'\x00' * N composes
            # cleanly with the BinOp [default] * size → Array.make
            # handler in expressions.py.
            return {
                "type": "ArrayLit",
                "elts": [{"type": "Number", "value": b}
                         for b in expr.value],
            }
        if expr.value is ...:
            return {"type": "Number", "value": 0}
        if isinstance(expr.value, complex):
            return {"type": "Number", "value": int(expr.value.real)}
        return {"type": "Number", "value": expr.value}

    def _py_expr_unaryop(self, expr: ast.UnaryOp) -> Dict[str, Any]:
        return {"type": "UnaryOp", "op": self._py_op_to_str(expr.op),
                "expr": self._py_expr_to_ir(expr.operand)}

    def _py_expr_binop(self, expr: ast.BinOp) -> Dict[str, Any]:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.op),
                "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.right)}

    def _py_expr_compare(self, expr: ast.Compare) -> Dict[str, Any]:
        return {"type": "BinOp", "op": self._py_op_to_str(expr.ops[0]),
                "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.comparators[0])}

    def _py_expr_boolop(self, expr: ast.BoolOp) -> Dict[str, Any]:
        op_str = "and" if isinstance(expr.op, ast.And) else "or"
        result = self._py_expr_to_ir(expr.values[0])
        for operand in expr.values[1:]:
            result = {"type": "BinOp", "op": op_str, "left": result, "right": self._py_expr_to_ir(operand)}
        return result

    def _py_expr_call(self, expr: ast.Call) -> Dict[str, Any]:
        if isinstance(expr.func, ast.Name):
            if expr.func.id == "deque":
                # collections-plan: `deque(...)` reduces to the list/array model. Lower
                # it to an empty array literal so it reuses the append/index/len
                # machinery verbatim (identical to `dq = []`). A seeded iterable is
                # modelled as empty (sound under-approximation); left-end ops
                # (appendleft/popleft) and pop are out of scope.
                return {"type": "ArrayLit", "elts": []}
            # typing-engagement ty1 / 26-0000-typing-spec-2 §2.2 (LR4):
            # `isinstance(v, Literal[...])` is not supported — `typing.Literal`
            # aliases are not valid second arguments to `isinstance` (PEP 586 /
            # CPython raises TypeError natively). Surface this as a clear
            # normalization-time rejection (mirroring the L4a bytes-literal
            # rejection) rather than letting it lower to an opaque uninterpreted
            # boolean that surfaces as a solver timeout. The shim must NOT make
            # `Literal[...]` a valid isinstance second argument (LR8).
            if (expr.func.id == "isinstance"
                    and len(expr.args) == 2
                    and isinstance(expr.args[1], ast.Subscript)
                    and isinstance(expr.args[1].value, ast.Name)
                    and expr.args[1].value.id == "Literal"):
                raise PyCSLIRError(
                    "isinstance: a typing.Literal alias is not a valid second "
                    "argument (LR4 / PEP 586 — use a concrete value equality test)",
                    stage="ir-emit")
            return {"type": "Call", "func": expr.func.id,
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args]}
        elif isinstance(expr.func, ast.Attribute):
            parts: List[str] = []
            node = expr.func
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                parts.append(node.id)
                parts.reverse()
                return {"type": "Call", "func": ".".join(parts),
                        "args": [self._py_expr_to_ir(arg) for arg in expr.args]}
            receiver_ir = self._py_expr_to_ir(node)
            parts.reverse()
            return {"type": "Call", "func": ".".join(parts),
                    "args": [self._py_expr_to_ir(arg) for arg in expr.args],
                    "receiver": receiver_ir}
        return {"type": "UnknownPyExpr"}

    def _py_expr_tuple(self, expr: ast.Tuple) -> Dict[str, Any]:
        return {"type": "Tuple", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_subscript(self, expr: ast.Subscript) -> Dict[str, Any]:
        value = self._py_expr_to_ir(expr.value)
        slice_node = expr.slice
        if isinstance(slice_node, ast.Index):
            slice_node = slice_node.value
        if isinstance(slice_node, ast.Slice):
            slice_ir = self._py_expr_to_ir(slice_node)
            return {"type": "SliceAccess", "value": value, "slice": slice_ir}
        index = self._py_expr_to_ir(slice_node)
        return {"type": "Subscript", "value": value, "index": index}

    def _py_expr_list(self, expr: ast.List) -> Dict[str, Any]:
        return {"type": "ArrayLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_attribute(self, expr: ast.Attribute) -> Dict[str, Any]:
        if isinstance(expr.value, ast.Name) and expr.value.id == 'self':
            return {"type": "FieldGet", "object": "self", "field": expr.attr}
        obj_ir = self._py_expr_to_ir(expr.value)
        return {"type": "Attribute", "object": obj_ir, "attr": expr.attr}

    def _py_expr_dict(self, expr: ast.Dict) -> Dict[str, Any]:
        keys = [self._py_expr_to_ir(k) if k else {"type": "None"} for k in expr.keys]
        values = [self._py_expr_to_ir(v) for v in expr.values]
        return {"type": "DictLit", "keys": keys, "values": values}

    def _py_expr_set(self, expr: ast.Set) -> Dict[str, Any]:
        return {"type": "SetLit", "elts": [self._py_expr_to_ir(e) for e in expr.elts]}

    def _py_expr_listcomp(self, expr: ast.ListComp) -> Dict[str, Any]:
        return {"type": "ListComp", "elt": self._py_expr_to_ir(expr.elt),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_setcomp(self, expr: ast.SetComp) -> Dict[str, Any]:
        return {"type": "SetComp", "elt": self._py_expr_to_ir(expr.elt),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_dictcomp(self, expr: ast.DictComp) -> Dict[str, Any]:
        return {"type": "DictComp", "key": self._py_expr_to_ir(expr.key),
                "value": self._py_expr_to_ir(expr.value),
                "generators": self._comprehension_generators_to_ir(expr.generators)}

    def _py_expr_fstring(self, expr: ast.JoinedStr) -> Dict[str, Any]:
        parts = []
        for v in expr.values:
            if isinstance(v, ast.Constant):
                parts.append({"type": "String", "value": str(v.value)})
            elif isinstance(v, ast.FormattedValue):
                parts.append(self._py_expr_to_ir(v.value))
            else:
                parts.append(self._py_expr_to_ir(v))
        return {"type": "FString", "parts": parts}

    def _py_expr_ifexp(self, expr: ast.IfExp) -> Dict[str, Any]:
        return {"type": "IfExpr", "test": self._py_expr_to_ir(expr.test),
                "body": self._py_expr_to_ir(expr.body),
                "orelse": self._py_expr_to_ir(expr.orelse)}

    def _py_expr_starred(self, expr: ast.Starred) -> Dict[str, Any]:
        return {"type": "Starred", "value": self._py_expr_to_ir(expr.value)}

    def _py_expr_walrus(self, expr: ast.NamedExpr) -> Dict[str, Any]:
        target_name = expr.target.id if isinstance(expr.target, ast.Name) else "_walrus"
        return {"type": "NamedExpr", "target": target_name,
                "value": self._py_expr_to_ir(expr.value)}

    def _py_expr_lambda(self, expr: ast.Lambda) -> Dict[str, Any]:
        params = [arg.arg for arg in expr.args.args]
        return {"type": "Lambda", "params": params,
                "body": self._py_expr_to_ir(expr.body)}

    def _py_expr_slice(self, expr: ast.Slice) -> Dict[str, Any]:
        lower = self._py_expr_to_ir(expr.lower) if expr.lower else None
        upper = self._py_expr_to_ir(expr.upper) if expr.upper else None
        step = self._py_expr_to_ir(expr.step) if expr.step else None
        return {"type": "Slice", "lower": lower, "upper": upper, "step": step}

    # Dispatch table: Python AST statement type → handler method name
    _PY_STMT_HANDLERS: Dict[type, str] = {
        ast.Assign:    "_py_stmt_assign",
        ast.AugAssign: "_py_stmt_augassign",
        ast.Return:    "_py_stmt_return",
        ast.While:     "_py_stmt_while",
        ast.For:       "_py_stmt_for",
        ast.If:        "_py_stmt_if",
        ast.Continue:  "_py_stmt_continue",
        ast.Assert:    "_py_stmt_assert",
        ast.Raise:     "_py_stmt_raise",
        ast.AnnAssign: "_py_stmt_annassign",
        ast.Expr:      "_py_stmt_expr",
        ast.Try:       "_py_stmt_try",
        ast.With:      "_py_stmt_with",
        ast.Pass:      "_py_stmt_pass",
        ast.Break:     "_py_stmt_break",
        ast.Delete:    "_py_stmt_delete",
    }

    # Dispatch table: Python AST operator type → operator string
    _PY_OP_MAP: Dict[type, str] = {
        ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "div",
        ast.Mod: "%",
        ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
        ast.USub: "-", ast.UAdd: "+", ast.Not: "not", ast.Invert: "~",
        ast.In: "in", ast.NotIn: "not in",
        ast.Is: "==", ast.IsNot: "!=",
        ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
        ast.LShift: "<<", ast.RShift: ">>", ast.Pow: "**",
    }

    def _py_stmts_to_ir(self, stmts: List[ast.stmt]) -> List[Dict[str, Any]]:
        ir_stmts: List[Dict[str, Any]] = []
        for stmt in stmts:
            for lname in getattr(stmt, 'csl_labels', []):
                ir_stmts.append({"stmt": "Label", "name": lname})
            for cp in getattr(stmt, 'csl_checkpoints', []):
                # `#@ assert P` / `#@ check P` — a real proof obligation before the
                # statement (distinct from the Python `assert` stmt, which is a no-op).
                pa = {"stmt": "ProofAssert", "kind": cp.kind,
                      "test": self._csl_to_ir(cp.expr)}
                origin = getattr(cp, "origin", None)
                if origin:                      # attribution for synthesized (e.g. HAPPY) checks
                    pa["origin"] = origin
                ir_stmts.append(pa)
            for ga in getattr(stmt, 'csl_ghost_assigns', []):
                ir_stmts.append(self._emit_ghost_assign(ga))
            handler_name = self._PY_STMT_HANDLERS.get(type(stmt))
            if handler_name is not None:
                result = getattr(self, handler_name)(stmt, ir_stmts)
            elif hasattr(ast, 'Match') and isinstance(stmt, ast.Match):
                self._py_stmt_match(stmt, ir_stmts)
            for ga in getattr(stmt, 'csl_trailing_ghost_assigns', []):
                ir_stmts.append(self._emit_ghost_assign(ga))
            # A `#@ assert`/`#@ check` that is the LAST statement of a block (block footer)
            # emits AFTER this statement — so it sits at the end of the enclosing block
            # (e.g. inside an `if`/loop body) where its variables are in scope. Without this
            # a trailing assert is silently dropped (Module3 now surfaces it as a trailing
            # checkpoint).
            for cp in getattr(stmt, 'csl_trailing_checkpoints', []):
                pa = {"stmt": "ProofAssert", "kind": cp.kind,
                      "test": self._csl_to_ir(cp.expr)}
                origin = getattr(cp, "origin", None)
                if origin:
                    pa["origin"] = origin
                ir_stmts.append(pa)
        return ir_stmts

    def _emit_ghost_assign(self, ga) -> Dict[str, Any]:
        """Build the IR dict for a ghost assignment (declaration or update). Shared by
        the leading (`csl_ghost_assigns`) and trailing (`csl_trailing_ghost_assigns`)
        emission loops."""
        if isinstance(ga, GhostArraySetDecl):
            return {"stmt": "GhostArraySet", "target": ga.target,
                    "index": self._csl_to_ir(ga.index),
                    "value": self._csl_to_ir(ga.value)}
        return {"stmt": "GhostAssign", "target": ga.target,
                "value": self._csl_to_ir(ga.value), "op": ga.op,
                "ghost_type": getattr(ga, 'declared_type', 'int')}

    def _py_stmt_assign(self, stmt: ast.Assign, ir_stmts: List[Dict[str, Any]]) -> None:
        target = stmt.targets[0]
        if isinstance(target, ast.Name):
            ir_stmts.append({"stmt": "Assign", "target": target.id, "value": self._py_expr_to_ir(stmt.value)})
        elif (isinstance(target, ast.Attribute) and
              isinstance(target.value, ast.Name) and
              target.value.id == 'self'):
            ir_stmts.append({"stmt": "FieldAssign", "object": "self", "field": target.attr,
                             "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(target, ast.Subscript):
            array_ir = self._py_expr_to_ir(target.value)
            slice_node = target.slice
            if isinstance(slice_node, ast.Index):
                slice_node = slice_node.value
            if isinstance(slice_node, ast.Slice):
                # `arr[lo:hi] = rhs` — slice (range) assignment. Lowered by
                # Module6 to a bounded `Array.blit` when rhs is array-typed.
                lower_ir = (self._py_expr_to_ir(slice_node.lower)
                            if slice_node.lower else {"type": "Number", "value": 0})
                upper_ir = (self._py_expr_to_ir(slice_node.upper)
                            if slice_node.upper else None)
                ir_stmts.append({"stmt": "ArraySliceSet", "array": array_ir,
                                 "lower": lower_ir, "upper": upper_ir,
                                 "value": self._py_expr_to_ir(stmt.value)})
            else:
                index_ir = self._py_expr_to_ir(slice_node)
                ir_stmts.append({"stmt": "ArraySet", "array": array_ir,
                                 "index": index_ir, "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(target, ast.Tuple):
            targets = [elt.id for elt in target.elts if isinstance(elt, ast.Name)]
            ir_stmts.append({"stmt": "TupleUnpack", "targets": targets,
                             "value": self._py_expr_to_ir(stmt.value)})

    def _py_stmt_augassign(self, stmt: ast.AugAssign, ir_stmts: List[Dict[str, Any]]) -> None:
        if isinstance(stmt.target, ast.Name):
            ir_stmts.append({"stmt": "AugAssign", "target": stmt.target.id,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif (isinstance(stmt.target, ast.Attribute) and
              isinstance(stmt.target.value, ast.Name) and
              stmt.target.value.id == 'self'):
            ir_stmts.append({"stmt": "FieldAugAssign", "object": "self", "field": stmt.target.attr,
                             "op": self._py_op_to_str(stmt.op), "value": self._py_expr_to_ir(stmt.value)})
        elif isinstance(stmt.target, ast.Subscript):
            # collections-plan: `c[k] op= v` (subscript augmented assignment) was
            # silently dropped (no arm here). Desugar to a plain subscript store of
            # `(c[k]) op v` — reusing the proven ArraySet path (→ map_update_some for
            # a dict / Counter, Array.set for a list). Also fixes `arr[i] += v`.
            slice_node = stmt.target.slice
            if isinstance(slice_node, ast.Index):  # <3.9 compatibility
                slice_node = slice_node.value
            if not isinstance(slice_node, ast.Slice):
                read_ir = self._py_expr_to_ir(stmt.target)  # c[k] (read)
                ir_stmts.append({
                    "stmt": "ArraySet",
                    "array": self._py_expr_to_ir(stmt.target.value),
                    "index": self._py_expr_to_ir(slice_node),
                    "value": {"type": "BinOp", "op": self._py_op_to_str(stmt.op),
                              "left": read_ir, "right": self._py_expr_to_ir(stmt.value)}})

    def _py_stmt_return(self, stmt: ast.Return, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Return", "value": self._py_expr_to_ir(stmt.value) if stmt.value else None})

    def _py_stmt_while(self, stmt: ast.While, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_while(stmt))

    def _py_stmt_for(self, stmt: ast.For, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_for(stmt))

    def _py_stmt_if(self, stmt: ast.If, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append(self._process_if(stmt))

    def _py_stmt_continue(self, stmt: ast.Continue, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Continue"})

    def _py_stmt_assert(self, stmt: ast.Assert, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_node: Dict[str, Any] = {"stmt": "Assert", "test": self._py_expr_to_ir(stmt.test)}
        if stmt.msg and isinstance(stmt.msg, ast.Constant) and isinstance(stmt.msg.value, str):
            ir_node["msg"] = stmt.msg.value
        ir_stmts.append(ir_node)

    def _py_stmt_raise(self, stmt: ast.Raise, ir_stmts: List[Dict[str, Any]]) -> None:
        exc_ir: Dict[str, Any] = {"stmt": "Raise", "exc_type": None, "exc_value": None}
        if stmt.exc is not None:
            if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                exc_ir["exc_type"] = stmt.exc.func.id
                if stmt.exc.args:
                    exc_ir["exc_value"] = self._py_expr_to_ir(stmt.exc.args[0])
            elif isinstance(stmt.exc, ast.Name):
                exc_ir["exc_type"] = stmt.exc.id
        ir_stmts.append(exc_ir)

    def _py_stmt_annassign(self, stmt: ast.AnnAssign, ir_stmts: List[Dict[str, Any]]) -> None:
        if isinstance(stmt.target, ast.Name) and stmt.value is not None:
            ir_stmts.append({"stmt": "Assign", "target": stmt.target.id,
                             "value": self._py_expr_to_ir(stmt.value)})

    def _py_stmt_expr(self, stmt: ast.Expr, ir_stmts: List[Dict[str, Any]]) -> None:
        # Skip bare string-literal expressions (docstrings) — no WhyML equivalent.
        if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            return
        ir_stmts.append({"stmt": "Expr", "value": self._py_expr_to_ir(stmt.value)})

    def _py_stmt_try(self, stmt: ast.Try, ir_stmts: List[Dict[str, Any]]) -> None:
        body_ir = self._py_stmts_to_ir(stmt.body)
        handlers = []
        for h in stmt.handlers:
            exc_type = None
            if h.type and isinstance(h.type, ast.Name):
                exc_type = h.type.id
            elif h.type and isinstance(h.type, ast.Tuple):
                exc_type = "|".join(
                    n.id for n in h.type.elts if isinstance(n, ast.Name))
            handlers.append({
                "exc_type": exc_type,
                "name": h.name,
                "body": self._py_stmts_to_ir(h.body)
            })
        ir_stmts.append({
            "stmt": "Try", "body": body_ir, "handlers": handlers,
            "orelse": self._py_stmts_to_ir(stmt.orelse),
            "finalbody": self._py_stmts_to_ir(stmt.finalbody)
        })

    def _py_stmt_with(self, stmt: ast.With, ir_stmts: List[Dict[str, Any]]) -> None:
        mutex = (getattr(stmt, 'csl_critical_mutex', None) or
                 getattr(stmt, 'csl_acquires', None))
        body_ir = self._py_stmts_to_ir(stmt.body)
        if mutex:
            inv = self._get_mutex_invariant_ir(mutex)
            ir_stmts.append({
                "stmt": "CriticalSection", "mutex": mutex, "body": body_ir,
                "assume_invariant": inv, "prove_invariant": inv,
            })
        else:
            ir_stmts.extend(body_ir)

    def _py_stmt_pass(self, stmt: ast.Pass, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Pass"})

    def _py_stmt_break(self, stmt: ast.Break, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Break"})

    def _py_stmt_delete(self, stmt: ast.Delete, ir_stmts: List[Dict[str, Any]]) -> None:
        ir_stmts.append({"stmt": "Pass"})  # model as no-op

    def _py_stmt_match(self, stmt: Any, ir_stmts: List[Dict[str, Any]]) -> None:
        subject_ir = self._py_expr_to_ir(stmt.subject)
        cases = []
        for case in stmt.cases:
            pattern_ir = self._match_pattern_to_ir(case.pattern)
            guard_ir = self._py_expr_to_ir(case.guard) if case.guard else None
            body_ir = self._py_stmts_to_ir(case.body)
            cases.append({"pattern": pattern_ir, "guard": guard_ir, "body": body_ir})
        ir_stmts.append({"stmt": "Match", "subject": subject_ir, "cases": cases})

    def _process_while(self, node: ast.While) -> Dict[str, Any]:
        return {
            "stmt": "While",
            # §4.4 statement-level span (refactor.md B4a) — the loop's source line, so
            # the core can report IR-level loop-invariant errors with the same
            # "while loop at line N" context Module4 produced. Module6 ignores it.
            "line": getattr(node, "lineno", 0),
            "test": self._py_expr_to_ir(node.test),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body)
        }

    def _process_for(self, node: ast.For) -> Dict[str, Any]:
        target = node.target.id if isinstance(node.target, ast.Name) else "_for_target"
        return {
            "stmt": "For",
            "line": getattr(node, "lineno", 0),  # §4.4 statement-level span (refactor.md B4a)
            "target": target,
            "iter": self._py_expr_to_ir(node.iter),
            "invariants": self._csl_list_to_ir(getattr(node, 'csl_invariants', [])),
            "variants": self._csl_list_to_ir(getattr(node, 'csl_variants', [])),
            "body": self._py_stmts_to_ir(node.body),
            # UB-7.1 opt-in (#@ allow_iteration_mutation). Module 4
            # consults this when running `find_iteration_mutations`.
            "allow_iteration_mutation": bool(getattr(node, 'csl_allow_iteration_mutation', False)),
            "lineno": getattr(node, "lineno", 0),
        }

    def _process_if(self, node: ast.If) -> Dict[str, Any]:
        return {
            "stmt": "If",
            "test": self._py_expr_to_ir(node.test),
            "body": self._py_stmts_to_ir(node.body),
            "orelse": self._py_stmts_to_ir(node.orelse)
        }

    def _match_pattern_to_ir(self, pattern: Any) -> Dict[str, Any]:
        """Translate a Python 3.10+ match pattern to IR."""
        if hasattr(ast, 'MatchValue') and isinstance(pattern, ast.MatchValue):
            return {"pattern": "Value", "value": self._py_expr_to_ir(pattern.value)}
        elif hasattr(ast, 'MatchSingleton') and isinstance(pattern, ast.MatchSingleton):
            if pattern.value is True:
                return {"pattern": "Value", "value": {"type": "Bool", "value": True}}
            elif pattern.value is False:
                return {"pattern": "Value", "value": {"type": "Bool", "value": False}}
            elif pattern.value is None:
                return {"pattern": "Value", "value": {"type": "None"}}
            return {"pattern": "Value", "value": {"type": "Number", "value": pattern.value}}
        elif hasattr(ast, 'MatchAs') and isinstance(pattern, ast.MatchAs):
            if pattern.name is None and pattern.pattern is None:
                return {"pattern": "Wildcard"}
            name = pattern.name if pattern.name else "_"
            if pattern.pattern:
                return {"pattern": "Capture", "name": name,
                        "inner": self._match_pattern_to_ir(pattern.pattern)}
            return {"pattern": "Capture", "name": name, "inner": None}
        elif hasattr(ast, 'MatchOr') and isinstance(pattern, ast.MatchOr):
            return {"pattern": "Or",
                    "alternatives": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        elif hasattr(ast, 'MatchSequence') and isinstance(pattern, ast.MatchSequence):
            return {"pattern": "Sequence",
                    "elts": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        elif hasattr(ast, 'MatchClass') and isinstance(pattern, ast.MatchClass):
            # sum-types: `case Ctor(p1, …):` — a constructor pattern with capture sub-patterns.
            ctor = pattern.cls.id if isinstance(pattern.cls, ast.Name) else "Unknown"
            return {"pattern": "Constructor", "ctor": ctor,
                    "captures": [self._match_pattern_to_ir(p) for p in pattern.patterns]}
        return {"pattern": "Unknown"}

    def _scan_2d_in_expr(self, expr: Dict[str, Any], param_names: Set[str], result: Set[str]) -> None:
        """Recursively scan an IR expression dict for a[i][j] access patterns."""
        if not isinstance(expr, dict):
            return
        t = expr.get("type", "")
        if t == "Subscript":
            inner = expr.get("value", {})
            if inner.get("type") == "Subscript":
                root = inner.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    # Exclude dict-style access (string indices) from 2D array detection
                    idx1 = inner.get("index", {})
                    idx2 = expr.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(inner, param_names, result)
            self._scan_2d_in_expr(expr.get("index", {}), param_names, result)
        elif t in ("BinOp",):
            self._scan_2d_in_expr(expr.get("left", {}), param_names, result)
            self._scan_2d_in_expr(expr.get("right", {}), param_names, result)
        elif t in ("UnaryOp",):
            self._scan_2d_in_expr(expr.get("expr", {}), param_names, result)
        elif t in ("Call",):
            for arg in expr.get("args", []):
                self._scan_2d_in_expr(arg, param_names, result)

    def _scan_2d_in_stmt(self, stmt: Dict[str, Any], param_names: Set[str], result: Set[str]) -> None:
        """Recursively scan an IR statement dict for a[i][j] access patterns."""
        s = stmt.get("stmt", "")
        if s == "ArraySet":
            arr = stmt.get("array", {})
            # a[i][j] = v  →  ArraySet(array=Subscript(Var(a), i), index=j, ...)
            if arr.get("type") == "Subscript":
                root = arr.get("value", {})
                if root.get("type") == "Var" and root.get("name") in param_names:
                    idx1 = arr.get("index", {})
                    idx2 = stmt.get("index", {})
                    if idx1.get("type") != "String" and idx2.get("type") != "String":
                        result.add(root["name"])
            self._scan_2d_in_expr(arr, param_names, result)
            self._scan_2d_in_expr(stmt.get("index", {}), param_names, result)
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("Assign", "AugAssign", "Return"):
            self._scan_2d_in_expr(stmt.get("value", {}), param_names, result)
        elif s in ("While", "For"):
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
        elif s == "If":
            self._scan_2d_in_expr(stmt.get("test", {}), param_names, result)
            for child in stmt.get("body", []):
                self._scan_2d_in_stmt(child, param_names, result)
            for child in stmt.get("orelse", []):
                self._scan_2d_in_stmt(child, param_names, result)

    def _collect_2d_params(self, body_ir: List[Dict[str, Any]],
                           param_names: Set[str]) -> List[str]:
        """Return sorted list of param names used as a[i][j] in the body IR."""
        result: Set[str] = set()
        for stmt in body_ir:
            self._scan_2d_in_stmt(stmt, param_names, result)
        return sorted(result)

    # --- 3. Main Traversal Hooks ---

    @staticmethod
    @staticmethod
    def _irnode_ann_name(annotation):
        """typed-ir-for-b-ceiling.md B-C2: the IR-node type name if `annotation` is
        `ExprIR`/`StmtIR`/`IRNode`/`ContractExprIR` — bare Name, forward-ref string, or
        `Optional[...]`-wrapped — else None. `emit_ir` is total, so `Optional[ExprIR]`
        maps to the same field/param type."""
        # Duck-type on `type(node).__name__`, NOT `isinstance(_, ast.Constant)`: the
        # frontend's AST nodes can come from a different `ast` module object than a local
        # `import ast`, so isinstance spuriously returns False (observed in practice).
        a = annotation
        if a is None:
            return None
        if type(a).__name__ == "Subscript" and type(getattr(a, "value", None)).__name__ == "Name" \
                and getattr(a.value, "id", None) == "Optional":
            a = getattr(a, "slice", a)
        tn = type(a).__name__
        if tn == "Constant" and isinstance(getattr(a, "value", None), str):
            nm = a.value
        elif tn == "Name":
            nm = getattr(a, "id", None)
        else:
            nm = None
        return nm if nm in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR") else None

    def _field_type_from_annotation(annotation: Optional[ast.expr]) -> str:
        """Lower a Python type annotation to the IR field-type tag.

        Bare names like `int`/`bool`/`str` are passed through (lowercased
        where appropriate). Parametric annotations recognise `List`/
        `Set`/`Dict`/`FrozenSet`/`Tuple` (head identifier, lowercased).
        `Optional[T]` and `Union[T, None]` unwrap to T. Everything else
        falls back to `int` (the legacy default)."""
        if annotation is None:
            return "int"
        if isinstance(annotation, ast.Name):
            name = annotation.id
            # Bare collection annotations on a field (`self.x: list`).
            # Mirrors the RHS-shape inference for plain assignments so an
            # annotated `array int` field resolves to "list" (→ `array int`
            # in the WhyML record), not the int default.
            if name in ("list", "tuple", "bytearray", "bytes"):
                return "list"
            if name == "dict":
                return "dict"
            if name in ("set", "frozenset"):
                return "set"
            if name == "str":
                # 07-2333-rev2 TP-3 (Gap 6): a `str` field is a faithful Why3 `string`
                # (the WhyML record emitter maps the "str" tag to `string`), not int.
                return "str"
            if name in ("int", "bool", "float"):
                return "int"
            # Unrecognised plain name — treat as int (e.g. user types).
            return "int"
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            head = annotation.value.id
            if head == "Optional":
                inner = annotation.slice
                if isinstance(inner, ast.Subscript) and isinstance(inner.value, ast.Name):
                    return inner.value.id.lower()
                return "int"
            if head == "Union":
                inner = annotation.slice
                if isinstance(inner, ast.Tuple):
                    for elt in inner.elts:
                        if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
                            return elt.value.id.lower()
                return "int"
            return head.lower()
        return "int"

    def _field_type_from_annotation_inst(self, annotation: Optional[ast.expr],
                                          scope_name: str = "") -> str:
        """Instance wrapper for `_field_type_from_annotation` that tries Final
        normalization first (resolving the inner type `τ(T)` — F3, no narrowing,
        typing-engagement ty1 / 27-0000-typing-spec-3), then Union normalization
        (synthesizing a per-site variant for `Union`/`Optional`/`|` field
        annotations), else falls back to the static legacy resolution. For
        non-Final/non-Union annotations, byte-identical."""
        if annotation is not None:
            if self._irnode_ann_name(annotation) is not None:
                return "ExprIR"          # typed-ir-for-b-ceiling.md B-C2 (field)
            try:
                fin_tag = self._normalize_final_annotation(annotation)
                if fin_tag is not None:
                    return fin_tag
            except Exception:
                pass
            if scope_name:
                try:
                    return self._normalize_union_annotation(annotation, scope_name)
                except Exception:
                    pass
        return self._field_type_from_annotation(annotation)

    @staticmethod
    def _mixin_field_type(type_str: str) -> str:
        """Map a `#@ shared_state`/`#@ touches_field` declared type to the record
        field type the type-decl emitter understands (the same coarsening used for
        __init__ fields): scalar/bool → `int`, containers keep their name."""
        t = (type_str or "int").strip()
        if t in ("list", "dict", "set", "frozenset", "tuple", "array", "string"):
            return "list" if t == "array" else t
        return "int"

    # --- TypedDict normalization (typing-engagement ty2 / 29-1700-typing-spec-5) ---
    #
    # `class Point(TypedDict): x: int; y: int` (PEP 589) is lowered at this seam
    # to a record `type_decl` with one field per declared key. Per the two-plane
    # spec §1 (T1–T9) and the core-agent hard rule (typing-global-impl.md §5,
    # TY2): a TypedDict class synthesizes a WhyML record `type td = { x: int;
    # y: int }`, field access `p["x"]` becomes record-field access `p.x`, and
    # construction `{"x": 1, "y": 2}` becomes a record literal. NO `\trusted`.
    # The `is_typeddict: True` flag is the ONLY new IR state — backward-
    # compatible (defaults False), so NO IR_VERSION bump. Consumed by Module 6's
    # subscript/dict-literal lowering and `core_ir_semantic`'s no-blend check.

    @staticmethod
    def _is_typeddict_class(node: ast.ClassDef) -> bool:
        """True iff `node` is `class X(TypedDict)` / `class X(TypedDict, total=...)`.

        Recognizes the bare head name `TypedDict` in `node.bases` (the
        import-rewriting in `import_classifier.py` canonicalizes
        `from typing import TypedDict`). A dotted `typing.TypedDict` base is
        also recognized. Byte-identical for non-TypedDict classes (pure base-name
        test)."""
        for b in node.bases:
            if isinstance(b, ast.Name) and b.id == "TypedDict":
                return True
            if isinstance(b, ast.Attribute) and b.attr == "TypedDict":
                return True
        return False

    # typing-engagement ty3 / 33-1700-typing-spec-9 — TypeVar/Generic (PEP 484 + PEP 695):
    # collect the type parameters of a generic class/function so the step-5
    # monomorphization IR-resolution pass can COLLECT concrete instantiations and
    # EMIT name-mangled specialized copies. This seam captures `class C[T]:`,
    # `def f[T]():` (PEP 695) and the legacy `class C(Generic[T])` / `TypeVar("T")`
    # spelling. ABSENT on non-generic decls → byte-identical for unaffected drivers
    # (additive IR v1.4 field). NO lowering here — the monomorphization pass does
    # the COLLECT/EMIT; Module 6 lowers the specialized copies as ordinary
    # monomorphic code.

    _GENERIC_BASE_NAMES = {"Generic"}

    def _collect_type_params(self, node) -> List[Dict[str, Any]]:
        """Return the IR `type_params` list for a generic ClassDef/FunctionDef, or
        `[]` if it is not generic. Each entry is `{"name": str, "bound": Optional[str],
        "kind": str}` where kind is "TypeVar" (the only interpreted kind —
        ParamSpec/TypeVarTuple are schema-only and loud-fail in the monomorphization
        pass, GT3). The PEP 695 `type_params` attribute is the primary source; the
        legacy `Generic[T]` base / `TypeVar("T", bound=B)` call is recognized too."""
        tparams = getattr(node, "type_params", None) or []
        out: List[Dict[str, Any]] = []
        for tp in tparams:
            kind = type(tp).__name__  # TypeVar / ParamSpec / TypeVarTuple
            name = getattr(tp, "name", None)
            bound = None
            bnode = getattr(tp, "bound", None)
            if isinstance(bnode, ast.Name):
                bound = bnode.id
            elif isinstance(bnode, ast.Attribute):
                bound = bnode.attr
            out.append({"name": name, "bound": bound, "kind": kind})
        # Legacy spelling: `class C(Generic[T])` where T was declared via
        # `T = TypeVar("T", bound=B)` at module scope. The PEP 695 `type_params`
        # is empty; the Generic[T] base carries the TypeVar name(s). We resolve
        # the names against the module's TypeVar-call registry (collected in
        # visit_Assign below) so the bound is recovered. Only the bare-Name form
        # is recognized (a generic base that is itself a Subscript on Generic).
        if not out and isinstance(node, ast.ClassDef):
            for b in node.bases:
                if (isinstance(b, ast.Subscript)
                        and isinstance(b.value, ast.Name)
                        and b.value.id in self._GENERIC_BASE_NAMES):
                    names = self._extract_generic_arg_names(b.slice)
                    registry = self.program_ir.get("typevar_registry") or {}
                    for nm in names:
                        info = registry.get(nm, {})
                        out.append({"name": nm,
                                    "bound": info.get("bound"),
                                    "kind": "TypeVar"})
                    break
        return out

    @staticmethod
    def _extract_generic_arg_names(slice_node) -> List[str]:
        """Extract the TypeVar names from `Generic[T]` / `Generic[T, U]` slice."""
        if isinstance(slice_node, ast.Name):
            return [slice_node.id]
        if isinstance(slice_node, ast.Tuple):
            names = []
            for elt in slice_node.elts:
                if isinstance(elt, ast.Name):
                    names.append(elt.id)
            return names
        return []

    def _collect_typevar_registry(self, node: ast.Module) -> Dict[str, Dict[str, Any]]:
        """Scan module-level assigns for `T = TypeVar("T"[, bound=B])` and return
        `{name: {"bound": Optional[str]}}`. The legacy PEP 484 spelling; the
        PEP 695 `class C[T]` form needs no registry (its `type_params` carry the
        bound directly)."""
        registry: Dict[str, Dict[str, Any]] = {}
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue
            call = stmt.value
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                continue
            if call.func.id != "TypeVar":
                continue
            name = target.id
            bound = None
            for kw in call.keywords:
                if kw.arg == "bound":
                    if isinstance(kw.value, ast.Name):
                        bound = kw.value.id
                    elif isinstance(kw.value, ast.Attribute):
                        bound = kw.value.attr
            registry[name] = {"bound": bound}
        return registry

    def _emit_typeddict_record(self, node: ast.ClassDef) -> None:
        """Synthesize a record `type_decl` for `class X(TypedDict): ...`.

        Walks the class body's AnnAssigns (the `x: int` field declarations,
        PEP 589 §"Class Syntax") and emits a record with one field per declared
        key. Per-key totality (PEP 655 `Required`/`NotRequired`, T1c) and
        class-level totality (`total=False`, T1b) are applied: a not-required
        key's type is `Optional[T]` (a `_union_<scope>_<idx>` variant with a
        `None` arm, reusing the TY1 Union normalization). The record carries NO
        `__init__`, NO class invariants, NO bases — it is a pure data record.
        Construction is via dict literals (Module 6 lowers them to record
        literals), not `__init__`."""
        scope_name = node.name
        total = True
        for kw in node.keywords:
            if kw.arg == "total" and isinstance(kw.value, ast.Constant):
                total = bool(kw.value.value)
        fields: List[Dict[str, Any]] = []
        field_defaults: Dict[str, int] = {}
        for child in node.body:
            if not (isinstance(child, ast.AnnAssign)
                    and isinstance(child.target, ast.Name)):
                continue
            fname = child.target.id
            ftype = self._typeddict_field_type(child.annotation, scope_name,
                                                total)
            fields.append({"name": fname, "type": ftype, "mutable": True})
            field_defaults[fname] = 0
        self.program_ir["type_decls"].append({
            "kind": "record", "name": node.name, "fields": fields,
            "mutable_state": self._is_mutable_state_decorated(node),
            "class_invariants": [], "field_defaults": field_defaults,
            "has_hash": False, "has_eq": False, "is_unhashable": False,
            "constants": {}, "bases": [],
            "init_params": [], "init_body": [], "init_ensures": [],
            "is_mixin": False, "compose_from": [],
            "is_typeddict": True,
        })
        self.program_ir.setdefault("constructors", {})
        self.program_ir["constructors"][node.name] = {"type": node.name,
                                                       "arity": 0}

    def _typeddict_field_type(self, annotation: ast.expr, scope_name: str,
                               total: bool) -> str:
        """Resolve a TypedDict field's annotation to its IR type tag, applying
        per-key totality (PEP 655) and class-level totality (PEP 589).

        - `Required[T]` → unwrap to `τ(T)` (required key, even in total=False).
        - `NotRequired[T]` → `Optional[τ(T)]` (not-required key, even in
          total=True).
        - In `total=False`, a plain `T` annotation becomes `Optional[T]`.
        - Otherwise resolve `τ(T)` via the existing Union/Final/Literal-aware
          resolver `_field_type_from_annotation_inst`."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id == "Required"):
            return self._field_type_from_annotation_inst(annotation.slice,
                                                         scope_name)
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id == "NotRequired"):
            return self._wrap_optional(annotation.slice, scope_name)
        if not total:
            return self._wrap_optional(annotation, scope_name)
        return self._field_type_from_annotation_inst(annotation, scope_name)

    def _wrap_optional(self, inner: ast.expr, scope_name: str) -> str:
        """Lower `Optional[T]` for a TypedDict field by synthesizing a
        `_union_<scope>_<idx>` variant with a `None` arm (reusing the TY1
        Union normalization)."""
        optional_ann = ast.Subscript(
            value=ast.Name(id="Optional", ctx=ast.Load()),
            slice=inner, ctx=ast.Load())
        try:
            return self._normalize_union_annotation(optional_ann, scope_name)
        except Exception:
            return self._field_type_from_annotation_inst(inner, scope_name)

    def _synthesize_typeddict_functional(self, node: ast.Module) -> None:
        """Recognize the functional form `Name = TypedDict("Name", {k: T, ...})`
        (PEP 589 §"Functional Syntax") and synthesize the same record type_decl
        as the class form. Best-effort: only literal `{"name": type}` dicts are
        recognized; a non-literal fields dict synthesizes nothing (byte-
        identical fallback — the assignment stays an opaque int)."""
        for stmt in node.body:
            if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Call)):
                continue
            call = stmt.value
            fn = call.func
            is_td = ((isinstance(fn, ast.Name) and fn.id == "TypedDict")
                     or (isinstance(fn, ast.Attribute)
                         and fn.attr == "TypedDict"))
            if not is_td or len(call.args) < 2:
                continue
            name_arg, fields_arg = call.args[0], call.args[1]
            if not (isinstance(name_arg, ast.Constant)
                    and isinstance(name_arg.value, str)):
                continue
            td_name = name_arg.value
            if not isinstance(fields_arg, ast.Dict):
                continue
            fields: List[Dict[str, Any]] = []
            field_defaults: Dict[str, int] = {}
            ok = True
            for k, v in zip(fields_arg.keys, fields_arg.values):
                if not (isinstance(k, ast.Constant)
                        and isinstance(k.value, str)):
                    ok = False
                    break
                ftype = self._field_type_from_annotation_inst(v, td_name)
                fields.append({"name": k.value, "type": ftype,
                               "mutable": True})
                field_defaults[k.value] = 0
            if not ok or not fields:
                continue
            self.program_ir["type_decls"].append({
                "kind": "record", "name": td_name, "fields": fields,
                "class_invariants": [], "field_defaults": field_defaults,
                "has_hash": False, "has_eq": False, "is_unhashable": False,
                "constants": {}, "bases": [],
                "init_params": [], "init_body": [], "init_ensures": [],
                "is_mixin": False, "compose_from": [],
                "is_typeddict": True,
            })
            self.program_ir.setdefault("constructors", {})
            self.program_ir["constructors"][td_name] = {"type": td_name,
                                                         "arity": 0}

    # typing-engagement ty2 / 30-1700-typing-spec-6: `class Point(NamedTuple)`
    # (PEP 526) is recognized at this seam and lowered to a record type_decl
    # with one field per declared key, in declaration order (positional index is
    # significant — N5 maps `p[i]` to the i-th field). Per the two-plane spec §1
    # (N1–N7) and the core-agent hard rule (typing-global-impl.md §5, TY2): a
    # NamedTuple class synthesizes a WhyML record `type nt = { x: int; y: int }`
    # (reusing the TypedDict record seam), named field access `p.x` becomes
    # record-field access, positional access `p[0]` becomes record-field access
    # by index, construction `Point(1, 2)` becomes a record literal. NO
    # `\trusted`. The `is_namedtuple: True` flag is the ONLY new IR state —
    # backward-compatible (defaults False), so NO IR_VERSION bump. Consumed by
    # Module 6's positional-subscript lowering and `core_ir_semantic`'s no-blend
    # check. The pre-existing `_synthesize_namedtuple_records` (functional
    # `collections.namedtuple` form, all-int fields) is NOT modified — it
    # handles a different factory.

    @staticmethod
    def _is_namedtuple_class(node: ast.ClassDef) -> bool:
        """True iff `node` is `class X(NamedTuple)` (PEP 526 class form).

        Recognizes the bare head name `NamedTuple` in `node.bases` (the
        import-rewriting in `import_classifier.py` canonicalizes
        `from typing import NamedTuple`). A dotted `typing.NamedTuple` base is
        also recognized. Byte-identical for non-NamedTuple classes (pure
        base-name test)."""
        for b in node.bases:
            if isinstance(b, ast.Name) and b.id == "NamedTuple":
                return True
            if isinstance(b, ast.Attribute) and b.attr == "NamedTuple":
                return True
        return False

    def _emit_namedtuple_record(self, node: ast.ClassDef) -> None:
        """Synthesize a record `type_decl` for `class X(NamedTuple): ...`.

        Walks the class body's AnnAssigns (the `x: int` field declarations,
        PEP 526 §"Custom Class Bodies") and emits a record with one field per
        declared field, in declaration order (order is significant for
        positional access N5). Field types are resolved via the existing
        Union/Optional/Final/Literal-aware resolver. A field with a default
        (N1b, `x: int = 0`) captures the default into `field_defaults`
        (int-valued per the existing convention; a non-int default falls back
        to 0). The record carries `init_params` (field names in order) and
        `init_body` (each field set from its same-named param) so positional
        construction `Point(1, 2)` reuses the EXISTING Tier-A parametrized
        record construction (`_call_record_constructor`) — emitting a record
        literal `{ x = 1; y = 2 }`. The record carries NO `__init__`, NO class
        invariants, NO bases — it is a pure data record."""
        scope_name = node.name
        fields: List[Dict[str, Any]] = []
        field_defaults: Dict[str, int] = {}
        init_params: List[str] = []
        init_body: List[Dict[str, Any]] = []
        for child in node.body:
            if not (isinstance(child, ast.AnnAssign)
                    and isinstance(child.target, ast.Name)):
                continue
            fname = child.target.id
            ftype = self._field_type_from_annotation_inst(child.annotation,
                                                           scope_name)
            _fld = {"name": fname, "type": ftype, "mutable": True}
            # self-field-dict-reflection (typed-ir-for-b-ceiling.md §12): record a
            # `dict[str, str]` field's VALUE type so `self.<field>.get(k)` reads back a
            # `string`, not the coarsened int (the class counterpart of the local dict ν).
            _vt = self._m5_get_dict_value_type(child.annotation)
            if _vt:
                _fld["value_type"] = _vt
            # i-feel-good.md I-E / self-ir-schema.md IR2: a `List[str]`→`array string` /
            # `List[StmtIR]`→`array emit_ir` field element type (consulted only in a
            # @mutable_state module; inert for the dict path).
            else:
                _le = self._m5_get_list_elem_type(child.annotation)
                # cf6.md M1.2: a `cases: List[Dict[...]]` field (local class-def path) → emit_ir.
                if _le is None and self._cf6_is_cases_list_of_dict(fname, child.annotation):
                    _le = "emit_ir"
                if _le is not None:
                    _fld["value_type"] = _le
            fields.append(_fld)
            # N1b: only fields with an explicit default value (x: int = 0)
            # populate `field_defaults`. A field WITHOUT a default is a
            # required positional argument (N7 — wrong arity is a static
            # error). The int-coded convention is used for the default value;
            # a non-int default falls back to 0 (sound — the field is set at
            # construction time, never read before write).
            if (child.value is not None
                    and isinstance(child.value, ast.Constant)
                    and isinstance(child.value.value, (int, float))):
                field_defaults[fname] = int(child.value.value)
            init_params.append(fname)
            init_body.append({"field": fname,
                              "value": {"type": "Var", "name": fname}})
        self.program_ir["type_decls"].append({
            "kind": "record", "name": node.name, "fields": fields,
            "mutable_state": self._is_mutable_state_decorated(node),
            "class_invariants": [], "field_defaults": field_defaults,
            "has_hash": False, "has_eq": False, "is_unhashable": False,
            "constants": {}, "bases": [],
            "init_params": init_params, "init_body": init_body,
            "init_ensures": [],
            "is_mixin": False, "compose_from": [],
            "is_namedtuple": True,
        })
        self.program_ir.setdefault("constructors", {})
        self.program_ir["constructors"][node.name] = {"type": node.name,
                                                        "arity": 0}

    def _synthesize_namedtuple_functional(self, node: ast.Module) -> None:
        """Recognize the functional form `Name = NamedTuple("Name", [(k, T), ...])`
        (PEP 484 §"NamedTuple") and synthesize the same record type_decl as the
        class form. Best-effort: only literal `[("name", type), ...]` lists are
        recognized; a non-literal fields list synthesizes nothing (byte-
        identical fallback — the assignment stays an opaque int)."""
        for stmt in node.body:
            if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Call)):
                continue
            call = stmt.value
            fn = call.func
            is_nt = ((isinstance(fn, ast.Name) and fn.id == "NamedTuple")
                     or (isinstance(fn, ast.Attribute)
                         and fn.attr == "NamedTuple"))
            if not is_nt or len(call.args) < 2:
                continue
            name_arg, fields_arg = call.args[0], call.args[1]
            if not (isinstance(name_arg, ast.Constant)
                    and isinstance(name_arg.value, str)):
                continue
            nt_name = name_arg.value
            if not isinstance(fields_arg, ast.List):
                continue
            fields: List[Dict[str, Any]] = []
            field_defaults: Dict[str, int] = {}
            init_params: List[str] = []
            init_body: List[Dict[str, Any]] = []
            ok = True
            for elt in fields_arg.elts:
                if not (isinstance(elt, ast.Tuple) and len(elt.elts) == 2):
                    ok = False
                    break
                k, v = elt.elts
                if not (isinstance(k, ast.Constant)
                        and isinstance(k.value, str)):
                    ok = False
                    break
                fname = k.value
                ftype = self._field_type_from_annotation_inst(v, nt_name)
                fields.append({"name": fname, "type": ftype,
                               "mutable": True})
                field_defaults[fname] = 0
                init_params.append(fname)
                init_body.append({"field": fname,
                                  "value": {"type": "Var", "name": fname}})
            if not ok or not fields:
                continue
            self.program_ir["type_decls"].append({
                "kind": "record", "name": nt_name, "fields": fields,
                "class_invariants": [], "field_defaults": field_defaults,
                "has_hash": False, "has_eq": False, "is_unhashable": False,
                "constants": {}, "bases": [],
                "init_params": init_params, "init_body": init_body,
                "init_ensures": [],
                "is_mixin": False, "compose_from": [],
                "is_namedtuple": True,
            })
            self.program_ir.setdefault("constructors", {})
            self.program_ir["constructors"][nt_name] = {"type": nt_name,
                                                           "arity": 0}

    # typing-engagement ty2 / 32-1700-typing-spec-8 — Protocol (PEP 544) helpers.
    # The static plane treats `class P(Protocol)` as a contract interface (a named
    # collection of method contracts): a marker record (`is_protocol: True`, no
    # fields) + each member emitted as an `abstract: True` function (a bodyless
    # `val` with its contract — the refinement TARGET). Conformance `C conforms to
    # P` (declared via `#@ conforms_to P`) populates the EXISTING `overrides` IR
    # list with `(C__m, P__m)` pairs; `--check-behavioral-subtyping` emits the
    # per-method refinement goal `((pre_P -> pre_C) /\\ (post_C -> post_P))` (P2/P4).
    # The runtime plane is the thin `runtime_checkable` shim (presence-only
    # isinstance, NO signature check — R3/R4). NO-BLEND (D1): the refinement goal
    # is a WhyML formula over the two contracts, NOT a runtime hasattr check.

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """True iff `node` is `class P(Protocol)` / `class P(typing.Protocol)` (PEP
        544). Recognizes the bare head name `Protocol` in `node.bases` (the
        import-rewriting in `import_classifier.py` already canonicalizes
        `from typing import Protocol`). A dotted `typing.Protocol` base is also
        recognized. Byte-identical for non-Protocol classes (pure base-name test)."""
        for b in node.bases:
            if isinstance(b, ast.Name) and b.id == "Protocol":
                return True
            if isinstance(b, ast.Attribute) and b.attr == "Protocol":
                return True
        return False

    def _emit_protocol_interface(self, node: ast.ClassDef) -> None:
        """Synthesize the contract interface for `class P(Protocol): ...` (P1).

        Emits (a) a marker record `type_decl` with `is_protocol: True` and NO
        fields (a protocol has no instance state — the record is the interface
        anchor), and (b) each protocol member `def m(self, ...) -> R: ...` as a
        function IR node with `abstract: True` (a bodyless `val` defined by its
        contract alone — the refinement TARGET, P1a). The member's
        `#@ ensures/requires/assigns` is the refinement target. Records the
        protocol's member names in `self._protocols[P]` for the conformance pass.

        `@runtime_checkable` (P1b) is a RUNTIME-plane marker; the static plane
        IGNORES it (it gates the runtime shim, §3 of the two-plane spec)."""
        proto_name = node.name
        self.program_ir["type_decls"].append({
            "kind": "record", "name": proto_name, "fields": [],
            "class_invariants": [], "field_defaults": {},
            "has_hash": False, "has_eq": False, "is_unhashable": False,
            "constants": {}, "bases": [],
            "init_params": [], "init_body": [], "init_ensures": [],
            "is_mixin": False, "compose_from": [],
            "is_protocol": True,
        })
        self.program_ir.setdefault("constructors", {})
        self.program_ir["constructors"][proto_name] = {"type": proto_name,
                                                        "arity": 0}
        members: Set[str] = set()
        self._current_class = proto_name
        for child in node.body:
            if not isinstance(child, ast.FunctionDef):
                continue
            if self._should_skip_method(child):
                continue
            member_ir = self._build_function_ir(child)
            # A protocol member is an abstract `val` defined by its contract —
            # the refinement TARGET (P1a). `abstract: True` emits a bodyless
            # `val` (sound uninterpreted op, NOT `\trusted`). The member's body
            # (`...`/`pass` by PEP 544 convention) is NOT lowered.
            member_ir["abstract"] = True
            member_ir["kind"] = "method"
            member_ir["self_type"] = proto_name
            member_ir["line"] = getattr(child, "lineno", 0)
            member_ir["col"] = getattr(child, "col_offset", 0)
            self.program_ir["functions"].append(member_ir)
            members.add(child.name)
        self._current_class = None
        self._protocols[proto_name] = members

    def _populate_protocol_conformance(self, node: ast.ClassDef) -> None:
        """Populate `overrides` for a `#@ conforms_to P` class (P2/P4).

        For each protocol `P` in `node.csl_conforms_to`, for each member `m` of
        `P`, find the conforming class's own method `C__m` and record an
        `(C__m, P__m)` override pair. The EXISTING `--check-behavioral-subtyping`
        emitter (`_render_refinement_goal`) discharges the per-method refinement
        goal `((pre_P -> pre_C) /\\ (post_C -> post_P))` — the per-method
        behavioural-refinement VC (P2). A class missing a member raises a static
        error (P3); a non-refining contract makes the goal unprovable (P3)."""
        conforms_to = list(getattr(node, 'csl_conforms_to', []) or [])
        if not conforms_to:
            return
        sub_name = node.name
        sub_lower = sub_name.lower()
        # The conforming class's own method names, namespaced `<sub>__<tail>`.
        own_methods: Set[str] = set()
        own_method_tails: Dict[str, str] = {}
        prefix_sub = f"{sub_lower}__"
        for fn in self.program_ir.get("functions", []):
            fname = fn.get("name", "")
            if fname.startswith(prefix_sub):
                tail = fname[len(prefix_sub):]
                own_methods.add(fname)
                own_method_tails[tail] = fname
        for proto_name in conforms_to:
            members = self._protocols.get(proto_name)
            if members is None:
                # P3: a conformance declaration against a non-protocol is a
                # static error (the target is not a recognized Protocol class).
                from errors import PyCSLSemanticError
                raise PyCSLSemanticError(
                    f"class '{sub_name}' (line {getattr(node, 'lineno', 0)}): "
                    f"`#@ conforms_to {proto_name}` but '{proto_name}' is not a "
                    f"recognized Protocol class. Conformance targets must be "
                    f"`class P(Protocol)` declarations in the same module.")
            proto_lower = proto_name.lower()
            for m in members:
                sub_method = own_method_tails.get(m)
                if sub_method is None:
                    # P3: a class missing a member fails conformance.
                    from errors import PyCSLSemanticError
                    raise PyCSLSemanticError(
                        f"class '{sub_name}' (line {getattr(node, 'lineno', 0)}): "
                        f"`#@ conforms_to {proto_name}` but '{sub_name}' does not "
                        f"provide member '{m}'. Conformance requires every protocol "
                        f"member to be present with a refining contract.")
                base_method = f"{proto_lower}__{m}"
                self.program_ir.setdefault("overrides", []).append({
                    "sub_method": sub_method, "base_method": base_method,
                    "sub_type": sub_lower, "base_type": proto_lower,
                })

    def _collect_class_fields(self, node: ast.ClassDef) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Extract mutable fields and default values from __init__.

        Returns (fields, field_defaults) where fields is a list of
        {"name", "type", "mutable"} dicts and field_defaults maps
        field names to their initial int values. Type annotations on
        `self.x: T = ...` declarations (AnnAssign) are extracted via
        `_field_type_from_annotation`; plain assignments default to
        `int`.
        """
        fields: List[Dict[str, Any]] = []
        field_names_seen: Set[str] = set()
        field_defaults: Dict[str, int] = {}
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for stmt in ast.walk(child):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (isinstance(target, ast.Attribute) and
                                    isinstance(target.value, ast.Name) and
                                    target.value.id == 'self' and
                                    target.attr not in field_names_seen):
                                # Infer type from RHS shape when no
                                # explicit annotation is present.
                                rhs = stmt.value
                                ftype = "int"
                                if isinstance(rhs, ast.Dict):
                                    ftype = "dict"
                                elif isinstance(rhs, ast.Set):
                                    ftype = "set"
                                elif isinstance(rhs, ast.List):
                                    ftype = "list"
                                elif isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name):
                                    if rhs.func.id in ("set", "frozenset", "dict", "list"):
                                        ftype = rhs.func.id
                                fields.append({"name": target.attr, "type": ftype, "mutable": True})
                                field_names_seen.add(target.attr)
                                if isinstance(rhs, ast.Constant) and isinstance(rhs.value, (int, float)):
                                    field_defaults[target.attr] = int(rhs.value)
                                else:
                                    sz = self._array_init_size(rhs)
                                    if sz is not None:
                                        field_defaults[target.attr] = sz
                    elif isinstance(stmt, ast.AnnAssign):
                        if (isinstance(stmt.target, ast.Attribute) and
                                isinstance(stmt.target.value, ast.Name) and
                                stmt.target.value.id == 'self' and
                                stmt.target.attr not in field_names_seen):
                            ftype = self._field_type_from_annotation_inst(
                                stmt.annotation, node.name)
                            fields.append({"name": stmt.target.attr, "type": ftype, "mutable": True})
                            field_names_seen.add(stmt.target.attr)
                            if (stmt.value and isinstance(stmt.value, ast.Constant) and
                                    isinstance(stmt.value.value, (int, float))):
                                field_defaults[stmt.target.attr] = int(stmt.value.value)
                            elif stmt.value is not None:
                                sz = self._array_init_size(stmt.value)
                                if sz is not None:
                                    field_defaults[stmt.target.attr] = sz
        # b14 B1 (ir-schema-spec.md): a `@dataclass` has no `__init__` — its
        # fields are CLASS-BODY AnnAssigns (`target: str`, `value: "ExprIR"`).
        # The synthesized `__init__` walk above finds none, so the class would
        # coarsen to the opaque `int` alias and `obj.field` would lower to an
        # abstract getattr. Collect the class-level AnnAssign fields here so a
        # dataclass registers as a record with typed (str → string) fields,
        # exactly like the TypedDict/NamedTuple paths. Additive: a non-dataclass
        # class is untouched, and no pre-existing corpus class is a @dataclass
        # (byte-identical fallback).
        if not fields and self._is_dataclass_decorated(node):
            for stmt in node.body:
                if (isinstance(stmt, ast.AnnAssign)
                        and isinstance(stmt.target, ast.Name)
                        and stmt.target.id not in field_names_seen):
                    ftype = self._field_type_from_annotation_inst(
                        stmt.annotation, node.name)
                    _fld2 = {"name": stmt.target.id, "type": ftype, "mutable": True}
                    # self-field-dict-reflection (typed-ir §12): a `dict[str, str]` field's
                    # value type, so `self.<field>.get(k)` reads a string.
                    _vt2 = self._m5_get_dict_value_type(stmt.annotation)
                    if _vt2:
                        _fld2["value_type"] = _vt2
                    else:
                        _le2 = self._m5_get_list_elem_type(stmt.annotation)
                        # cf6.md M1.2: MatchStmt.cases (imported @dataclass) → array emit_ir.
                        if _le2 is None and self._cf6_is_cases_list_of_dict(
                                stmt.target.id, stmt.annotation):
                            _le2 = "emit_ir"
                        if _le2 is not None:
                            _fld2["value_type"] = _le2
                    fields.append(_fld2)
                    field_names_seen.add(stmt.target.id)
                    if (stmt.value is not None and isinstance(stmt.value, ast.Constant)
                            and isinstance(stmt.value.value, (int, float))):
                        field_defaults[stmt.target.id] = int(stmt.value.value)
        return fields, field_defaults

    @staticmethod
    def _is_dataclass_decorated(node: ast.ClassDef) -> bool:
        """True if `node` carries a `@dataclass` / `@dataclass(...)` /
        `@dataclasses.dataclass` decorator (b14 B1 record registration)."""
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Name) and target.id == "dataclass":
                return True
            if isinstance(target, ast.Attribute) and target.attr == "dataclass":
                return True
        return False

    @staticmethod
    def _is_mutable_state_decorated(node: ast.ClassDef) -> bool:
        """mutable-self-plan.md M.2: True if `node` carries the `@mutable_state`
        decorator — the opt-in marker for CHECKED-`assigns` shared mutable state.
        A method of such a class emits its `#@ assigns self.x` as a WhyML `writes`
        clause on the concrete `let` (M.4), so Why3 checks the frame (non-vacuity).
        Absent on every existing class → byte-identical."""
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Name) and target.id == "mutable_state":
                return True
            if isinstance(target, ast.Attribute) and target.attr == "mutable_state":
                return True
        return False

    @staticmethod
    def _array_init_size(rhs: ast.expr) -> Optional[int]:
        """Literal initial LENGTH of an array/list-valued RHS, else None.
        Recognises `bytearray(N)` / `list([0]*N)`-style calls, `[v] * N` /
        `N * [v]`, and a list/bytes literal. For a list/array FIELD this length
        is stored in `field_defaults` so record construction (`C()`) emits
        `Array.make <len> 0` (matching the field's `\\length` class invariant),
        rather than the int fallback `0`."""
        # bytearray(N) / bytes(N)
        if (isinstance(rhs, ast.Call) and isinstance(rhs.func, ast.Name)
                and rhs.func.id in ("bytearray", "bytes") and len(rhs.args) == 1):
            return PyCSLToJSONEmitter._const_int_value(rhs.args[0])
        # [v] * N  or  N * [v]
        if isinstance(rhs, ast.BinOp) and isinstance(rhs.op, ast.Mult):
            for a, b in ((rhs.left, rhs.right), (rhs.right, rhs.left)):
                if isinstance(a, ast.List):
                    n = PyCSLToJSONEmitter._const_int_value(b)
                    if n is not None:
                        return max(len(a.elts), 1) * n if a.elts else n
        # [e1, e2, ...]  /  b"..."
        if isinstance(rhs, ast.List):
            return len(rhs.elts)
        if isinstance(rhs, ast.Constant) and isinstance(rhs.value, bytes):
            return len(rhs.value)
        return None

    @staticmethod
    def _const_int_value(value: ast.expr) -> Optional[int]:
        """Return the int value of a constant expr (incl. unary -N), else None."""
        if isinstance(value, ast.Constant) and isinstance(value.value, int) \
                and not isinstance(value.value, bool):
            return int(value.value)
        if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)
                and isinstance(value.operand.value, int)
                and not isinstance(value.operand.value, bool)):
            return -int(value.operand.value)
        return None

    def _collect_class_constants(self, node: ast.ClassDef,
                                 field_names: Set[str]) -> Dict[str, int]:
        """Collect class-body integer constants (`CAP = 64`, `O_EXCL = 128`).

        Only top-level `Name = <int literal>` / `Name: T = <int literal>`
        assignments in the class body are taken; names already used as
        instance fields (from __init__) are skipped. These let `self.CONST`
        lower to its literal in Module 6 instead of an opaque getattr.
        """
        constants: Dict[str, int] = {}
        for child in node.body:
            target: Optional[str] = None
            value: Optional[ast.expr] = None
            if (isinstance(child, ast.Assign) and len(child.targets) == 1
                    and isinstance(child.targets[0], ast.Name)):
                target = child.targets[0].id
                value = child.value
            elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                target = child.target.id
                value = child.value
            if target is None or value is None or target in field_names:
                continue
            iv = self._const_int_value(value)
            if iv is not None:
                constants[target] = iv
        return constants

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Collect fields from __init__, extract class invariants, record base
        classes, and emit a type_decl record.

        Inheritance (Layer B+C) is applied as a separate IR→IR pass
        (`_apply_inheritance` in pycsl.py) AFTER cross-module import resolution,
        so a base class defined in another module is available before the merge.
        Here we only record the base names.

        typing-engagement ty2 / 29-1700-typing-spec-5: a `class Point(TypedDict)`
        declaration is recognized at this seam and lowered to a record type_decl
        with one field per declared key (per the two-plane spec §1, T1–T9). The
        static plane is the record (Interpreted); the runtime plane is the
        plain-dict alias (Shimmed). NO `\trusted`. The `is_typeddict: True` flag
        gates Module 6's subscript/literal lowering paths.
        """
        if self._is_typeddict_class(node):
            self._emit_typeddict_record(node)
            self.generic_visit(node)
            return
        # typing-engagement ty2 / 30-1700-typing-spec-6: a `class Point(NamedTuple)`
        # declaration (PEP 526) is recognized here and lowered to a record
        # type_decl with one field per declared key, in declaration order
        # (per the two-plane spec §1, N1–N7). The static plane is the record
        # (Interpreted); the runtime plane is the plain-tuple alias (Shimmed).
        # NO `\trusted`. The `is_namedtuple: True` flag gates Module 6's
        # positional-subscript lowering path.
        if self._is_namedtuple_class(node):
            self._emit_namedtuple_record(node)
            self.generic_visit(node)
            return
        # typing-engagement ty2 / 32-1700-typing-spec-8: a `class P(Protocol)`
        # declaration (PEP 544) is recognized here and lowered to a contract
        # interface (a marker record `is_protocol: True` + each member emitted as
        # an `abstract: True` function — the refinement target, P1/P1a). The
        # static plane is the contract interface (Interpreted); the runtime plane
        # is the thin `runtime_checkable` shim (Shimmed). NO `\trusted`.
        if self._is_protocol_class(node):
            self._emit_protocol_interface(node)
            # NOTE: no `generic_visit(node)` — the protocol members are emitted
            # explicitly by `_emit_protocol_interface` (as `abstract: True` vals).
            # `generic_visit` would re-visit each member FunctionDef and emit it
            # AGAIN as a regular function (double emission). The protocol class
            # body carries ONLY member declarations (no nested classes / assigns
            # that need visiting), so skipping the walk is correct.
            return
        self._current_class = node.name
        fields, field_defaults = self._collect_class_fields(node)
        # Capture both `class X(Base)` (ast.Name) and `class X(mod.Base)`
        # (ast.Attribute, e.g. `ast.NodeVisitor`) — for the dotted form we
        # record the attribute tail (`NodeVisitor`); cross-module resolution
        # (pycsl._resolve_imports) injects the named class from a module import.
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)
        # UB-7.2 — track presence of __hash__ / __eq__ so Module 6 can
        # emit the consistency goal in the preamble.
        method_names = {
            s.name for s in node.body if isinstance(s, ast.FunctionDef)
        }
        has_hash = "__hash__" in method_names
        has_eq = "__eq__" in method_names
        # Mixin composition (Tier 1). Record the composition at MODULE level (not on a
        # type_decl) so a method-only composer with no own fields stays an opaque
        # `type c = int` — its provided methods are cloned in as `(self: c)` functions
        # by `_apply_composition` (pycsl.py), no record needed unless it has real state.
        is_mixin = bool(getattr(node, 'csl_is_mixin', False))
        compose_from = list(getattr(node, 'csl_compose_from', []) or [])
        if compose_from:
            self.program_ir.setdefault("compositions", []).append(
                {"composer": node.name, "mixins": compose_from})
        # Stateful mixin (Tier-1 stateful composition): a `#@ mixin` whose methods
        # declare `#@ shared_state`/`#@ touches_field` fields but has no __init__ of
        # its own must still emit as a RECORD (not the opaque `type c = int`), so its
        # provided methods' `self.<field>` accesses type-check in isolation (S1
        # verify-once) and after they are cloned into the composer. Merge the declared
        # fields into `fields` (dedup by name; __init__ fields win).
        if is_mixin:
            seen = {f["name"] for f in fields}
            for m in node.body:
                if not isinstance(m, ast.FunctionDef):
                    continue
                for s in (list(getattr(m, 'csl_mixin_shared_state', []) or [])
                          + list(getattr(m, 'csl_touches_field', []) or [])):
                    if s.name in seen:
                        continue
                    seen.add(s.name)
                    fields.append({"name": s.name,
                                   "type": self._mixin_field_type(s.type_str),
                                   "mutable": True})
                    field_defaults.setdefault(s.name, 0)
        if fields or bases:
            class_invariants_ir = [self._csl_to_ir(inv.expr)
                                   for inv in getattr(node, 'csl_class_invariants', [])]
            field_witness = {f["name"]: field_defaults.get(f["name"], 0) for f in fields}
            constants = self._collect_class_constants(node, {f["name"] for f in fields})
            init_params, init_body = self._collect_init_construction(node)
            init_ensures = self._collect_init_ensures(node)
            self.program_ir["type_decls"].append({
                "kind": "record", "name": node.name, "fields": fields,
            "mutable_state": self._is_mutable_state_decorated(node),
                "mutable_state": self._is_mutable_state_decorated(node),
                "class_invariants": class_invariants_ir, "field_defaults": field_witness,
                "has_hash": has_hash, "has_eq": has_eq,
                "is_unhashable": has_eq and not has_hash,
                "constants": constants, "bases": bases,
                "init_params": init_params, "init_body": init_body,
                "init_ensures": init_ensures,
                "is_mixin": is_mixin, "compose_from": compose_from,
                # typing-engagement ty3 / 33-1700-typing-spec-9: PEP 695 type
                # parameters of a generic class (`class C[T]:`) or the legacy
                # `TypeVar`/`Generic` spelling. ABSENT on non-generic classes
                # (emitted only when non-empty → byte-identical for unaffected
                # drivers, additive IR v1.4). Consumed by the monomorphization
                # IR-resolution pass (frontend/monomorphize.apply_monomorphization).
                **({"type_params": self._collect_type_params(node)}
                   if getattr(node, "type_params", None) else {}),
            })
        self.generic_visit(node)
        # typing-engagement ty2 / 32-1700-typing-spec-8: populate the per-method
        # conformance `overrides` for a `#@ conforms_to P` class AFTER the class's
        # own methods have been emitted (so `C__m` is in `program_ir["functions"]`).
        # This records `(C__m, P__m)` pairs; `--check-behavioral-subtyping`
        # discharges the per-method refinement goal (P2/P4). Byte-identical for
        # classes without `csl_conforms_to` (the population is a no-op).
        self._populate_protocol_conformance(node)
        self._current_class = None

    def _should_skip_method(self, node: ast.FunctionDef) -> bool:
        """Return True if this method should be skipped (dunders, @property)."""
        if not self._current_class:
            return False
        if node.name.startswith('__') and node.name.endswith('__'):
            return True
        if any(isinstance(d, ast.Name) and d.id == 'property'
               for d in node.decorator_list):
            return True
        return False

    # --- refactor.md B-final wedge: Module5 builds the IR symbol_table itself ---
    #
    # Ported verbatim from Module4_SemanticAnalyzer (`_get_type_name`,
    # `_get_dict_value_type`, `_get_dict_key_type`, and the body of
    # `_build_function_scope`) so Module5 no longer reads `node.csl_symbol_table`
    # / `node.csl_dict_value_types` / `node.csl_dict_key_types`. The resulting
    # tables are CONTENT- AND ORDER-IDENTICAL to Module4's, keeping the emitted
    # `.mlw` byte-for-byte unchanged.

    # --- Union normalization (typing-engagement ty1 / 25-1700-typing-spec-1) ---
    #
    # `Union[A, B]`, `Optional[X]`, `A | B`, and degenerate `Union[X]` are
    # desugared at this seam into a per-annotation-site synthesized `type_decl`
    # of kind "variant" (one constructor per arm; `None` → nullary `Arm_None`),
    # registered under a fresh variant name `_union_<func>_<idx>`. The symbol-
    # table entry for the variable is set to that variant name so the EXISTING
    # `_variant_types` branches in functions.py resolve it. For any annotation
    # that is NOT one of the four Union surface forms, the helper returns the
    # existing IR tag UNCHANGED, so every unaffected driver stays byte-identical.
    # `Any` arms are dropped (GT1) and recorded for --soundness-report.

    _UNION_ARM_TAGS = {"int", "bool", "str", "bytes", "float", "list", "dict", "set"}

    def _union_arm_tag(self, elt: ast.expr) -> Optional[str]:
        """Lower one Union arm AST to an IR type tag, or None if it is `Any`
        (GT1 — dropped) / unrecognised. `None` (the singleton) is returned as
        the sentinel string "None" so the caller can emit a nullary ctor."""
        if isinstance(elt, ast.Constant) and elt.value is None:
            return "None"
        if isinstance(elt, ast.Name):
            if elt.id == "None":
                return "None"
            if elt.id == "Any":
                return "Any"
            if elt.id in ("int", "bool", "float", "str", "bytes",
                          "list", "dict", "set", "frozenset", "tuple", "bytearray"):
                return "int" if elt.id in ("int", "bool") else elt.id
            return "Any"
        if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
            head = elt.value.id
            if head in ("List", "list"):
                return "list"
            if head in ("Dict", "dict"):
                return "dict"
            if head in ("Set", "set", "FrozenSet", "frozenset"):
                return "set"
            if head in ("Tuple", "tuple"):
                return "list"
            if head in ("Bytes", "bytes", "ByteArray", "bytearray"):
                return "list"
            return "Any"
        return "Any"

    def _collect_union_arms(self, ann_expr: ast.expr) -> Optional[List[ast.expr]]:
        """Return the list of arm AST expressions if `ann_expr` is one of the
        four Union surface forms, else None (caller falls back to existing
        logic). Flattens nested `|` (left-assoc BinOp BitOr) and degenerate
        `Union[X]` (non-Tuple slice)."""
        if isinstance(ann_expr, ast.Subscript) and isinstance(ann_expr.value, ast.Name):
            head = ann_expr.value.id
            if head == "Union":
                inner = ann_expr.slice
                if isinstance(inner, ast.Tuple):
                    return list(inner.elts)
                return [inner]
            if head == "Optional":
                inner = ann_expr.slice
                return [inner, ast.Constant(value=None)]
        if isinstance(ann_expr, ast.BinOp) and isinstance(ann_expr.op, ast.BitOr):
            arms: List[ast.expr] = []
            stack = [ann_expr]
            while stack:
                node = stack.pop()
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                    stack.append(node.right)
                    stack.append(node.left)
                else:
                    arms.append(node)
            arms.reverse()
            return arms
        return None

    def _normalize_union_annotation(self, ann_expr: ast.expr,
                                    scope_name: str) -> str:
        """Recognize `Union`/`Optional`/`|` annotations and synthesize a per-site
        variant `type_decl`. Returns the variant name (registered in
        `symbol_table` and `program_ir["type_decls"]`), OR the existing IR tag
        for non-Union annotations (byte-identical fallback).

        `scope_name` is the enclosing function/method name used for deterministic
        per-site mangling (`_union_<func>_<idx>`)."""
        arms_ast = self._collect_union_arms(ann_expr)
        if arms_ast is None:
            return self._m5_get_type_name_legacy(ann_expr)
        # Lower each arm, de-duplicate (C1a), drop Any (C4/GT1), order by source
        # with None last (C1b rendering detail).
        lowered: List[Tuple[str, str]] = []  # (tag, ctor-suffix-source)
        seen_tags: Set[str] = set()
        any_dropped = False
        none_present = False
        for elt in arms_ast:
            tag = self._union_arm_tag(elt)
            if tag == "Any":
                any_dropped = True
                continue
            if tag == "None":
                none_present = True
                continue
            if tag in seen_tags:
                continue
            seen_tags.add(tag)
            lowered.append((tag, elt))
        if none_present and "None" not in seen_tags:
            seen_tags.add("None")
        # Degenerate single-arm Union with no None (C1c): `Union[X]` is `X`.
        if len(lowered) == 1 and not none_present and not any_dropped:
            return self._m5_get_type_name_legacy(arms_ast[0])
        if not lowered and not none_present:
            # All arms were Any — refuse to synthesize a universal sink.
            return "int"
        idx = self._fresh_var_counter
        self._fresh_var_counter += 1
        safe_scope = "".join(c if c.isalnum() else "_" for c in scope_name) or "anon"
        variant_name = f"_union_{safe_scope}_{idx}"
        # Build the variant constructors: one per arm tag + a nullary Arm_None.
        # Constructor names are mangled per-variant (`Arm_<idx>_<i>`) so they
        # are globally unique within the Why3 module (Why3 constructors share
        # one namespace, so two variants cannot both have `Arm_0`).
        constructors = []
        for i, (tag, _elt) in enumerate(lowered):
            ctor_name = f"Arm_{idx}_{i}"
            payload = [tag]
            constructors.append({"name": ctor_name, "arity": 1, "payload": payload})
        if none_present:
            constructors.append({"name": f"Arm_{idx}_None", "arity": 0, "payload": []})
        self.program_ir["type_decls"].append({
            "kind": "variant",
            "name": variant_name,
            "type_params": [],
            "constructors": constructors,
        })
        self.program_ir.setdefault("constructors", {})
        for c in constructors:
            self.program_ir["constructors"][c["name"]] = {
                "type": variant_name, "arity": c["arity"]}
        if any_dropped:
            self.program_ir.setdefault("union_gt1_sites", []).append(variant_name)
        return variant_name

    # --- Final normalization (typing-engagement ty1 / 27-0000-typing-spec-3) ---
    #
    # `Final[T]` (PEP 591) is lowered at this seam to the degenerate single-
    # attribute, single-writer form of HAPPY's no-write confinement. The
    # annotation's *type* is the inner type `T` (F3 — no narrowing): the helper
    # returns `τ(T)` (resolved via the legacy tag resolver on the slice), or
    # `"Any"` for bare `Final`. The *write-policy* is recorded in a per-module
    # `final_registry` (collected by `_collect_final_registry` from `visit_Module`)
    # and discharged by the static-semantics check `core_ir_semantic._check_final`
    # — NOT by a VC. For any annotation that is NOT `Final[T]` / bare `Final`,
    # the helper returns `None` and the caller falls back to the existing logic
    # (byte-identical emission for every unaffected driver). NO new IR node, NO
    # IR_VERSION bump, NO new VC kind.

    @staticmethod
    def _is_final_annotation(ann_expr: ast.expr) -> bool:
        """True iff `ann_expr` is `Final[T]` (Subscript value=Name "Final") or
        bare `Final` (Name "Final")."""
        if isinstance(ann_expr, ast.Name) and ann_expr.id == "Final":
            return True
        return (isinstance(ann_expr, ast.Subscript)
                and isinstance(ann_expr.value, ast.Name)
                and ann_expr.value.id == "Final")

    def _normalize_final_annotation(self, ann_expr: ast.expr) -> Optional[str]:
        """Recognize `Final[T]` / bare `Final` (PEP 591) and return the inner
        type tag `τ(T)` (F3 — no narrowing; `Final` adds a write-restriction,
        NOT a type refinement). For bare `Final` (no slice), returns `"Any"`
        (PEP 591 permits an inferred type; PyCSL's monomorphic tag system has no
        inference, so the type is the opaque `Any` — sound: the name carries the
        write-restriction but no type refinement). Returns `None` for a non-Final
        annotation (caller falls back to existing logic — byte-identical).

        typing-engagement ty1 / 27-0000-typing-spec-3 §1.3: the write-policy
        itself (F1 write-once / F2 __init__-only) is NOT synthesized here — it
        is recorded in the per-module `final_registry` by
        `_collect_final_registry` and discharged by `core_ir_semantic._check_final`
        (a static write-site check, NOT a VC). This helper resolves ONLY the type
        tag (F3)."""
        if isinstance(ann_expr, ast.Name) and ann_expr.id == "Final":
            # Bare `Final` — no inner type. Return the opaque `Any` tag (sound:
            # the name carries the write-restriction but no type refinement).
            return "Any"
        if (isinstance(ann_expr, ast.Subscript)
                and isinstance(ann_expr.value, ast.Name)
                and ann_expr.value.id == "Final"):
            # `Final[T]` — the type is τ(T) (F3: Final does not narrow). Resolve
            # the inner type via the legacy tag resolver (so `Final[int]` → "int",
            # `Final[str]` → "str", `Final[MyClass]` → "myclass"). A nested
            # `Final[Final[int]]` resolves the inner `Final[int]` via this same
            # path → "Any" (the inner Final's bare-name fallback is not reached
            # because the inner is a Subscript, handled above → returns τ(int)).
            return self._m5_get_type_name_legacy(ann_expr.slice)
        return None

    def _collect_final_registry(self, module_node: ast.Module) -> None:
        """Walk the module AST for Final-annotated names and record each in
        `self._final_registry` with its allowed writer (the degenerate HAPPY
        single-attribute, single-writer form).

        - **F1 (module-level Final):** a top-level `AnnAssign` whose target is a
          `Name` and whose annotation is Final → `{"name", "kind": "module",
          "class": None, "allowed_writer": None}`. The declaration write is the
          ONLY permitted write; `allowed_writer: None` encodes "no function may
          write this name" (any function-body write is a reassignment).
        - **F2 (instance-attribute Final):** a class-body `AnnAssign` whose
          target is a `Name` (the `attr: Final[T]` declaration form, F2a — the
          declaration is NOT a write) → `{"name", "kind": "class_attr",
          "class": <ClassName>, "allowed_writer": "__init__"}`. Also records the
          `self.attr: Final[T]` form inside a class's `__init__` (same registry
          shape; the attribute is owned by the enclosing class).

        The registry is plumbed into `program_ir["final_registry"]` by
        `visit_Module` (omitted when empty → byte-identical for Final-free
        modules). Consumed by `core_ir_semantic._check_final`."""
        for stmt in module_node.body:
            # F1: module-level Final (`x: Final[int] = 5` or `x: Final[int]`).
            if (isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and self._is_final_annotation(stmt.annotation)):
                self._final_registry.append({
                    "name": stmt.target.id, "kind": "module",
                    "class": None, "allowed_writer": None,
                })
            # F2: class-body Final instance-attribute declarations.
            if isinstance(stmt, ast.ClassDef):
                for cstmt in stmt.body:
                    # `attr: Final[T]` (with or without value) in the class body.
                    if (isinstance(cstmt, ast.AnnAssign)
                            and isinstance(cstmt.target, ast.Name)
                            and self._is_final_annotation(cstmt.annotation)):
                        self._final_registry.append({
                            "name": cstmt.target.id, "kind": "class_attr",
                            "class": stmt.name, "allowed_writer": "__init__",
                        })
                    # `self.attr: Final[T]` inside the class's own __init__.
                    if (isinstance(cstmt, ast.FunctionDef)
                            and cstmt.name == "__init__"):
                        for sub in ast.walk(cstmt):
                            if (isinstance(sub, ast.AnnAssign)
                                    and isinstance(sub.target, ast.Attribute)
                                    and isinstance(sub.target.value, ast.Name)
                                    and sub.target.value.id == "self"
                                    and self._is_final_annotation(sub.annotation)):
                                self._final_registry.append({
                                    "name": sub.target.attr, "kind": "class_attr",
                                    "class": stmt.name,
                                    "allowed_writer": "__init__",
                                })

    def _normalize_literal_annotation(self, ann_expr: ast.expr,
                                       param_name: str) -> Optional[str]:
        """Recognize `Literal[v1, ..., vn]` (PEP 586) and synthesize a ground
        `requires` (parameter) or `ensures` (return) clause. Returns the base
        type tag (`"int"` or `"str"`) for a Literal annotation, or `None` for a
        non-Literal annotation (caller falls back to existing logic — byte-identical).

        typing-engagement ty1 / 26-0000-typing-spec-2 §1.3: the value-set
        obligation (L1) lowers to `requires { x = v1 \\/ ... \\/ x = vn }` (a
        ground requires, per the two-plane spec §1.6). L4 restricts literal
        kinds to int/str/bool/None; L4a rejects bytes; L5c rejects nested
        Literal / non-literal forms. L5a de-duplicates; L5b is the degenerate
        single-value case (bare `=`, no `\\/`). Mixed-kind literals (int + str)
        are rejected (PyCSL monomorphic parameter types — sound stricter-than-S1).

        `param_name` is the parameter name (for `requires x == v`), or
        `"\\result"` for a return annotation (synthesizes `ensures` instead).
        The synthesized IR expr is appended to `self._cur_literal_requires`
        (parameter) or `self._cur_literal_ensures` (return)."""
        if not (isinstance(ann_expr, ast.Subscript)
                and isinstance(ann_expr.value, ast.Name)
                and ann_expr.value.id == "Literal"):
            return None
        inner = ann_expr.slice
        val_elts: List[ast.expr] = (
            list(inner.elts) if isinstance(inner, ast.Tuple) else [inner])
        if not val_elts:
            raise PyCSLIRError(
                "Literal: empty value set is not supported (L1 / PEP 586)",
                stage="ir-emit")
        # Step 2 (L4/L4a/L4b/L5c): classify each literal; reject unsupported kinds.
        # Each entry is (kind, value, ir_node) where kind ∈ {"int", "str"}.
        classified: List[Tuple[str, Any, Dict[str, Any]]] = []
        for elt in val_elts:
            kind, value, ir_node = self._classify_literal_value(elt)
            classified.append((kind, value, ir_node))
        # Step 4: derive the base type tag; reject mixed-kind.
        kinds = {k for k, _v, _ir in classified}
        if len(kinds) > 1:
            raise PyCSLIRError(
                "Literal: mixed-kind literals (int + str) are not supported "
                "(PyCSL monomorphic parameter types — L4 / PEP 586)",
                stage="ir-emit")
        base_tag = "str" if kinds == {"str"} else "int"
        # Step 3 (L5a): de-duplicate by (kind, value); preserve source order (L5).
        seen: Set[Tuple[str, Any]] = set()
        deduped: List[Dict[str, Any]] = []
        for kind, value, ir_node in classified:
            key = (kind, value)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(ir_node)
        # Step 5: synthesize the disjunction (or bare `==` for the degenerate
        # single-value case, L5b). The param/\\result reference uses the `Result`
        # IR node for return annotations (matching `_csl_to_ir(CSLResult)` —
        # `{"type": "Result"}`), or a `Var` IR node for parameter annotations.
        if param_name == "\\result":
            var_node = {"type": "Result"}
            # Return annotation: synthesize an `ensures \result == v1 \/ ...`.
            # The `==` IR node shape matches a hand-written `#@ ensures \result == v`.
            clauses: List[Dict[str, Any]] = [
                {"type": "BinOp", "op": "==", "left": var_node, "right": v}
                for v in deduped]
            if len(clauses) == 1:
                self._cur_literal_ensures.append(clauses[0])
            else:
                acc = clauses[0]
                for c in clauses[1:]:
                    acc = {"type": "BinOp", "op": "or", "left": acc, "right": c}
                self._cur_literal_ensures.append(acc)
        else:
            var_node = {"type": "Var", "name": param_name}
            # Parameter annotation: synthesize a `requires x == v1 \/ ...`.
            clauses = [
                {"type": "BinOp", "op": "==", "left": var_node, "right": v}
                for v in deduped]
            if len(clauses) == 1:
                self._cur_literal_requires.append(clauses[0])
            else:
                acc = clauses[0]
                for c in clauses[1:]:
                    acc = {"type": "BinOp", "op": "or", "left": acc, "right": c}
                self._cur_literal_requires.append(acc)
        return base_tag

    @staticmethod
    def _classify_literal_value(elt: ast.expr) -> Tuple[str, Any, Dict[str, Any]]:
        """Classify one Literal value AST into (kind, python_value, ir_node).

        `kind` is `"int"` (for int/bool/None — the IR's int universe) or
        `"str"`. `ir_node` is the IR literal node (`Number`/`String`/`Bool`/
        `None`) that `_expr_to_whyml` will lower to the WhyML literal. Raises
        `PyCSLIRError` for unsupported kinds (L4a bytes, L4b Enum, L5c nested
        Literal, non-literal forms)."""
        # ast.Constant covers `1`, `"a"`, `True`, `False`, `None`, `b"x"`.
        if isinstance(elt, ast.Constant):
            v = elt.value
            if v is None:
                # Literal[None] — the singleton type of None. The IR's None
                # convention is int 0 (None → 0 in the int universe). Emit a
                # Number node so the `==` binop lowers to `x = 0` directly
                # (byte-stable; matches the existing `x == None` path).
                return ("int", None, {"type": "Number", "value": 0})
            if isinstance(v, bool):
                # bool is a subtype of int; IR encodes True→1, False→0.
                return ("int", v, {"type": "Bool", "value": v})
            if isinstance(v, int):
                return ("int", v, {"type": "Number", "value": v})
            if isinstance(v, str):
                return ("str", v, {"type": "String", "value": v})
            if isinstance(v, bytes):
                # L4a: bytes literals are NOT supported (PEP 586 restriction).
                raise PyCSLIRError(
                    "Literal: bytes literals are not supported "
                    "(L4a / PEP 586)", stage="ir-emit")
            # Any other Constant kind (float, complex, Ellipsis, ...) — reject.
            raise PyCSLIRError(
                f"Literal: unsupported literal kind {type(v).__name__} "
                "(L4 / PEP 586 — only int/str/bool/None supported)",
                stage="ir-emit")
        # `Literal[None]` spelled with the bare name (PEP 586 permits both).
        if isinstance(elt, ast.Name):
            if elt.id == "None":
                return ("int", None, {"type": "Number", "value": 0})
            if elt.id == "True":
                return ("int", True, {"type": "Bool", "value": True})
            if elt.id == "False":
                return ("int", False, {"type": "Bool", "value": False})
            # Any other Name (including nested Literal[Literal[...]] which is a
            # Subscript, handled below) — reject (L4b Enum, L5c nested, or a
            # non-literal Name).
            raise PyCSLIRError(
                f"Literal: unsupported value '{elt.id}' "
                "(L4 / L5c / PEP 586 — only int/str/bool/None literals supported)",
                stage="ir-emit")
        # A Subscript here is `Literal[Literal[...]]` (L5c) or
        # `Literal[Color.RED]` (L4b Enum) — both rejected.
        raise PyCSLIRError(
            "Literal: only int/str/bool/None literals are supported "
            "(L4 / L5c / PEP 586 — nested Literal and Enum members are not)",
            stage="ir-emit")

    def _m5_get_type_name_legacy(self, annotation: ast.expr) -> str:
        """The pre-Union `_m5_get_type_name` body, preserved verbatim so
        `_normalize_union_annotation` can fall back to it for non-Union
        annotations (byte-identical emission)."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Subscript) and isinstance(annotation.value, ast.Name):
            head = annotation.value.id
            if head == "Optional":
                inner = annotation.slice
                if isinstance(inner, ast.Name):
                    return inner.id
                if isinstance(inner, ast.Subscript) and isinstance(inner.value, ast.Name):
                    return inner.value.id.lower()
                return "Any"
            if head == "Union":
                inner = annotation.slice
                if isinstance(inner, ast.Tuple):
                    for elt in inner.elts:
                        if isinstance(elt, ast.Constant) and elt.value is None:
                            continue
                        if isinstance(elt, ast.Name) and elt.id != "None":
                            return elt.id
                        if isinstance(elt, ast.Subscript) and isinstance(elt.value, ast.Name):
                            return elt.value.id.lower()
                return "Any"
            if head == "Callable":
                # typing-engagement ty3 / 34-1700-typing-spec-10: `Callable[[A1,
                # ..., An], R]` (PEP 484) on a parameter is a function-type
                # obligation (C1). The arg-list + return type are encoded into
                # the existing symbol_table value as "callable:<a1>,...-><r>"
                # (a new tag VALUE, NOT a new IR field → no IR_VERSION bump).
                # Module 6's _param_type_str parses this into a curried WhyML
                # arrow type; the call site `f(a1, ..., an)` already lowers to
                # WhyML application. Triggers ONLY on head == "Callable" →
                # byte-identical for every non-Callable driver.
                return self._encode_callable_annotation(annotation)
            return head.lower()
        return "Any"

    # typing-engagement ty3 / 34-1700-typing-spec-10 — Callable (PEP 484) helpers.
    # The static plane treats `f: Callable[[A1, ..., An], R]` as a function-type
    # obligation (C1): the parameter is a value of function type. The arg-list +
    # return type are encoded into the existing symbol_table value string as
    # "callable:<a1>,<a2>,...-><r>" (a new tag VALUE, NOT a new IR field → no
    # IR_VERSION bump). Module 6's _param_type_str parses this into a curried
    # WhyML arrow type; the call site `f(a1, ..., an)` already lowers to WhyML
    # application. The runtime plane is the thin `Callable` shim (an
    # introspectable alias object, NO signature check — R1/R3). NO-BLEND (D1):
    # the static function-type obligation is a WhyML arrow parameter + Why3
    # typecheck, NOT a runtime callable() presence check.

    # The set of PyCSL primitive tags admissible as a Callable arg/return type
    # (C5 — stricter than S1, sound). bytes is excluded (modeled as a two-param
    # (loc, len) — not a single arrow type); list/dict/set excluded (not value-
    # semantic arrow domains in this delivery); Any refused (GT1).
    _CALLABLE_SCALAR_TAGS = frozenset({"int", "bool", "str", "float"})

    def _encode_callable_annotation(self, annotation: ast.Subscript) -> str:
        """Encode `Callable[[A1, ..., An], R]` as `"callable:<a1>,...-><r>"`.

        The slice is `Tuple([List([A1, ..., An]), R])` (PEP 484). Each Ai and R
        must resolve to a primitive scalar tag (`int`/`bool`/`str`/`float`) or a
        bare record/variant class name (a `Name` node). Anything else (bytes,
        list/dict/set, Any, a nested Callable, ParamSpec-derived `...`,
        `Concatenate[...]`) is a loud-fail `PYCSL-TY3-CALLABLE-SCOPE` (C5 sound
        scope limit, stricter than S1). Returns the encoded tag string."""
        from errors import PyCSLSemanticError
        slice_node = annotation.slice
        # The arg-list + return are a 2-tuple: ([A1, ..., An], R).
        if not (isinstance(slice_node, ast.Tuple) and len(slice_node.elts) == 2):
            raise PyCSLSemanticError(
                "Callable annotation must be `Callable[[A1, ..., An], R]` — "
                "the ellipsis form `Callable[..., R]` and ParamSpec-derived "
                "forms are not interpreted (GT3: ParamSpec is schema-only; "
                "C5 sound scope limit).",
                stage="ir-emit", code="PYCSL-TY3-CALLABLE-SCOPE",
            )
        arg_list_node, ret_node = slice_node.elts
        if not isinstance(arg_list_node, ast.List):
            raise PyCSLSemanticError(
                "Callable annotation's first argument must be a literal list "
                "[A1, ..., An] of argument types.",
                stage="ir-emit", code="PYCSL-TY3-CALLABLE-SCOPE",
            )
        arg_tags = [self._callable_type_tag(a) for a in arg_list_node.elts]
        ret_tag = self._callable_type_tag(ret_node)
        return f"callable:{','.join(arg_tags)}->{ret_tag}"

    def _callable_type_tag(self, node: ast.expr) -> str:
        """Resolve a single Callable arg/return type node to a PyCSL tag.

        Accepted: a `Name` whose id is a primitive scalar (`int`/`bool`/`str`/
        `float`) or a bare class name (record/variant — resolved by Module 6
        against `_record_types`/`_variant_types`). Refused: `Any` (GT1), a
        nested `Callable`/Subscript (C5), and anything not a bare Name."""
        from errors import PyCSLSemanticError
        if isinstance(node, ast.Name):
            tag = node.id
            if tag == "Any":
                raise PyCSLSemanticError(
                    "Callable arg/return type `Any` is refused — GT1: Any "
                    "never instantiates a function-type obligation (the "
                    "consistency relation is deliberately unsound).",
                    stage="ir-emit", code="PYCSL-TY3-GT1",
                )
            # Primitive scalar OR a bare class name (record/variant) — Module 6
            # resolves the class name against the known record/variant types.
            return tag
        if isinstance(node, ast.Subscript):
            raise PyCSLSemanticError(
                "A nested generic/Callable arg or return type is not "
                "interpreted (C5 sound scope limit, stricter than S1). "
                "Callable arg/return types must be bare primitive or class "
                "names in this delivery.",
                stage="ir-emit", code="PYCSL-TY3-CALLABLE-SCOPE",
            )
        raise PyCSLSemanticError(
            f"Callable arg/return type must be a bare Name (got "
            f"{type(node).__name__}) — C5 sound scope limit.",
            stage="ir-emit", code="PYCSL-TY3-CALLABLE-SCOPE",
        )

    def _m5_get_type_name(self, annotation: ast.expr,
                          scope_name: str = "",
                          param_name: str = "") -> str:
        """Public entry: try Final normalization first (resolving the inner type
        tag `τ(T)` — F3, no narrowing), then Literal normalization (synthesizing
        a ground `requires` clause), then Union normalization (synthesizing a
        per-site variant `type_decl`), else fall back to the legacy tag
        resolution. For non-Final/non-Literal/non-Union annotations the result is
        byte-identical to the pre-typing-engagement `_m5_get_type_name`.
        `scope_name` seeds the deterministic variant-name mangling; empty is
        tolerated (used by callers that cannot supply a function name, e.g. field
        annotations — those synthesize `_union_anon_*` which is still
        deterministic per-file). `param_name` is the parameter name for Literal
        `requires` synthesis (typing-engagement ty1 / 26-0000-typing-spec-2);
        empty means the caller is a field/local annotation, in which case
        Literal is NOT synthesized (a local `Literal` claim is unchecked on
        locals — see §1.3 step 6 / §8 Q3 of the spec).

        typing-engagement ty1 / 27-0000-typing-spec-3: `Final[T]` resolves to
        `τ(T)` (F3) BEFORE Literal/Union so a `Final[Literal[1, 2]]`-style
        annotation would resolve the inner Literal first (the Final is a
        write-restriction wrapper, not a type wrapper). The Final write-policy
        itself (F1/F2) is NOT synthesized here — it is recorded in the per-module
        `final_registry` (`_collect_final_registry` from `visit_Module`) and
        discharged by `core_ir_semantic._check_final` (a static write-site
        check, NOT a VC)."""
        # Final first: `Final[T]` → τ(T); bare `Final` → "Any". Returns None for
        # non-Final annotations (byte-identical fall-through). A Final
        # recognition bug MUST NOT perturb a non-Final driver — fall back to the
        # legacy path (byte-identical) on any non-PyCSLIRError exception.
        if self._irnode_ann_name(annotation) is not None:
            return "ExprIR"              # typed-ir-for-b-ceiling.md B-C2 (param)
        try:
            fin_tag = self._normalize_final_annotation(annotation)
            if fin_tag is not None:
                return fin_tag
        except PyCSLIRError:
            raise
        except Exception:
            pass
        if param_name:
            try:
                lit_tag = self._normalize_literal_annotation(annotation, param_name)
                if lit_tag is not None:
                    return lit_tag
            except PyCSLIRError:
                raise
            except Exception:
                # Never let a Literal-recognition bug perturb a non-Literal
                # driver: fall back to the legacy path (byte-identical) on any
                # non-PyCSLIRError exception. PyCSLIRError (L4a/L5c rejections)
                # MUST propagate — they are deliberate static rejections.
                pass
        if scope_name:
            try:
                return self._normalize_union_annotation(annotation, scope_name)
            except Exception:
                # Never let a Union-recognition bug perturb a non-Union driver:
                # fall back to the legacy path (byte-identical) on any error.
                pass
        return self._m5_get_type_name_legacy(annotation)

    @staticmethod
    def _cf6_is_cases_list_of_dict(field_name, annotation) -> bool:
        """cf6.md M1.2: True iff `field_name == "cases"` and `annotation` is `List[Dict[...]]`
        — the MatchStmt case list, reflectable as `array emit_ir`. GATED to the `cases` field
        name so OTHER `List[Dict]` fields (e.g. TryStmt.handlers) stay int-opaque (the CF5-safe
        choice). Byte-safe: the corpus has no `cases: List[Dict[...]]` record field."""
        if field_name != "cases" or annotation is None:
            return False
        if type(annotation).__name__ != "Subscript" \
                or type(getattr(annotation, "value", None)).__name__ != "Name" \
                or getattr(annotation.value, "id", None) not in ("List", "list"):
            return False
        sl = getattr(annotation, "slice", None)
        if type(sl).__name__ == "Index":
            sl = getattr(sl, "value", sl)
        return (type(sl).__name__ == "Subscript"
                and type(getattr(sl, "value", None)).__name__ == "Name"
                and getattr(sl.value, "id", None) in ("Dict", "dict"))

    @staticmethod
    def _m5_get_list_elem_type(annotation: ast.expr) -> Optional[str]:
        """i-feel-good.md I-B: the element type of a `List[str]`/`list[str]` annotation,
        as a WhyML tag ("string"); None for any other annotation. Used to type a
        string-list param `array string` (the abstract self-call val) instead of the
        collapsed `array int`. Only `str` elements are captured (the emitter's list
        plumbing is over WhyML identifiers / code fragments)."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("List", "list")):
            sl = annotation.slice
            if isinstance(sl, ast.Index):          # py<3.9 compat
                sl = sl.value
            # the element name — a bare `List[str]` (Name) OR a forward-ref
            # `List["StmtIR"]` (Constant string, e.g. the imported IR dataclasses).
            _en = None
            if isinstance(sl, ast.Name):
                _en = sl.id
            elif isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                _en = sl.value
            if _en == "str":
                return "string"
            # self-ir-schema.md IR2: a `List[StmtIR]`/`List[ExprIR]` field is `array emit_ir`
            # (the emit_ir IR-node sum), so a `body_stmts[-1]` read is an emit_ir node.
            if _en in ("StmtIR", "ExprIR", "IRNode", "ContractExprIR"):
                return "emit_ir"
        return None

    @staticmethod
    def _m5_get_dict_value_type(annotation: ast.expr) -> Optional[str]:
        """Port of Module4._get_dict_value_type. See that method for the rules."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("Dict", "dict")
                and isinstance(annotation.slice, ast.Tuple)
                and len(annotation.slice.elts) == 2):
            v = annotation.slice.elts[1]
            if isinstance(v, ast.Name) and v.id == "str":
                return "string"
            if (isinstance(v, ast.Subscript)
                    and isinstance(v.value, ast.Name)
                    and v.value.id in ("Dict", "dict")
                    and isinstance(v.slice, ast.Tuple)
                    and len(v.slice.elts) == 2):
                _ki, vi = v.slice.elts
                vw = "string" if (isinstance(vi, ast.Name) and vi.id == "str") else "int"
                # nested-map.md: the INNER map is int-keyed (str keys hashed via `str_hash_op`),
                # matching the model's uniform `dict[str,_] ~ map int (option _)` convention, so
                # membership/subscript on the inner map hash the key the same way as the outer.
                return f"map int (option {vw})"
            if (isinstance(v, ast.Subscript)
                    and isinstance(v.value, ast.Name)
                    and v.value.id in ("List", "list")
                    and isinstance(v.slice, ast.Name)):
                # nested-map.md / #15: `Dict[str, List[T]]` — the value is a `seq T` (a list
                # lowers to `seq`), so the field is `map int (option (seq T))`. `List[str]`→`seq
                # string` (was unhandled → flattened to int); `List[int]`→`seq int` (unchanged).
                return "seq string" if v.slice.id == "str" else "seq int"
        return None

    @staticmethod
    def _m5_get_dict_key_type(annotation: ast.expr) -> Optional[str]:
        """Port of Module4._get_dict_key_type. See that method for the rules."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("Dict", "dict")
                and isinstance(annotation.slice, ast.Tuple)
                and len(annotation.slice.elts) == 2):
            k = annotation.slice.elts[0]
            if isinstance(k, ast.Name) and k.id == "str":
                return "string"
        return None

    def _build_function_symbol_table(
        self, node: ast.FunctionDef
    ) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
        """Build (symbol_table, dict_value_types, dict_key_types) from the
        FunctionDef AST, reproducing Module4._build_function_scope's exact logic
        and INSERTION ORDER. The returned `symbol_table` still includes `'self'`
        if present (the caller strips it, matching the prior copy-from-Module4
        behaviour). Mirrors Module4: args (skip 'self') → Assign/AnnAssign/For
        locals (skip shared vars) → ghost-var declarations."""
        scope: Dict[str, str] = {}
        dict_value_types: Dict[str, str] = {}
        dict_key_types: Dict[str, str] = {}
        shared = self._shared_var_names
        _scope_name = node.name

        # Function arguments (skip 'self' for methods)
        param_annotations: Dict[str, str] = {}
        param_list_elem_types: Dict[str, str] = {}
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            # self-tcb-reduction T1.a: an `Optional[Dict[K,V]]` param is modeled as the `Dict[K,V]`
            # (None ≡ empty map), so `if subst and name in subst: subst[name]` types as string-map
            # ops instead of a Union variant. Byte-safe: 0 corpus methods have an Optional[Dict] param.
            _eff_ann = arg.annotation
            # self-tcb-reduction T1.a (E-2): a QUOTED IR-subclass forward-ref param
            # (`node: "UnaryOpExpr"`) resolves to that class's record (fields `op`/`expr`), like the
            # statement mirror's bare `stmt: AssignStmt`. Byte-safe: the corpus has no quoted
            # `*Expr`/`*Stmt` param annotation.
            if (isinstance(arg.annotation, ast.Constant)
                    and isinstance(arg.annotation.value, str)
                    and (arg.annotation.value.endswith("Expr")
                         or arg.annotation.value.endswith("Stmt"))):
                _eff_ann = ast.Name(id=arg.annotation.value)
            if (isinstance(arg.annotation, ast.Subscript)
                    and isinstance(arg.annotation.value, ast.Name)
                    and arg.annotation.value.id == "Optional"):
                _inner = arg.annotation.slice
                if type(_inner).__name__ == "Index":
                    _inner = _inner.value
                if (isinstance(_inner, ast.Subscript) and isinstance(_inner.value, ast.Name)
                        and _inner.value.id in ("Dict", "dict")):
                    _eff_ann = _inner
            arg_type = (self._m5_get_type_name(_eff_ann, _scope_name, arg.arg)
                        if _eff_ann else "Any")
            # self-tcb-reduction T1.a: an IR-node-typed PARAM (`node: "ExprIR"`, `stmt: "StmtIR"`)
            # is `emit_ir` — so the `_handle_*_expr` handlers reflect on it (`name_of node`).
            # Byte-safe: no corpus method annotates a param with the IR-node base names.
            if arg.annotation is not None and self._irnode_ann_name(arg.annotation) is not None:
                arg_type = self._irnode_ann_name(arg.annotation)
            scope[arg.arg] = arg_type
            # i-feel-good.md I-B: capture a `List[str]`/`list[str]` param's ELEMENT type
            # (string) so the abstract self-call val can type it `array string` instead of
            # the collapsed `array int` — WITHOUT changing `scope` (byte-safe; only the
            # @mutable_state param-type builder consults this map).
            if arg.annotation is not None:
                _le = self._m5_get_list_elem_type(arg.annotation)
                if _le is not None:
                    param_list_elem_types[arg.arg] = _le
            # no-more-int emitter L4b: preserve the param's annotated type as a
            # scalar-dict field on the func IR (like `return_annotation`), so it
            # survives import injection — which rebuilds `symbol_table` with `Any`
            # params for a cross-tree stub, losing `name: str`. A consumer merges
            # these back for `Any` params (functions._reset_function_state).
            if arg_type not in (None, "Any"):
                param_annotations[arg.arg] = arg_type
            if _eff_ann is not None:
                nu = self._m5_get_dict_value_type(_eff_ann)
                if nu is not None:
                    dict_value_types[arg.arg] = nu
                kappa = self._m5_get_dict_key_type(_eff_ann)
                if kappa is not None:
                    dict_key_types[arg.arg] = kappa

        # Local variables (skip shared module-level variables)
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id not in shared:
                        scope[target.id] = "Any"
                        # local-dict-value-type: a `d = {"a": "x", ...}` literal with all-STRING
                        # values is a `dict[_, str]`, so `d[k]` reads a `string` (default "") not the
                        # int default. Infer the value type from a homogeneous string-valued DictLit
                        # (a class-constant lookup table used LOCALLY, e.g. `_quant_binder_whyml`'s
                        # `scalars`). No annotation needed. Byte-identical for int-valued dict locals.
                        if (isinstance(child.value, ast.Dict) and child.value.values
                                and all(isinstance(v, ast.Constant) and isinstance(v.value, str)
                                        for v in child.value.values)):
                            dict_value_types[target.id] = "string"
                        # cleared-hash.md S1(a): a dict LITERAL with all-STRING keys
                        # (`d = {"a": 1, "b": 2}`) is string-keyed (κ = string) → it
                        # lowers to `map string (option ν)` with native `String.(=)`,
                        # NOT `map int` + the opaque `str_hash_op`. `None` keys (a
                        # sparse literal) do not count; a homogeneous string-key
                        # literal is the safe, unambiguous signal. Does not override
                        # an explicit annotation (setdefault below runs only if
                        # unset). Int-keyed literals are unchanged.
                        if (isinstance(child.value, ast.Dict) and child.value.keys
                                and all(isinstance(k, ast.Constant) and isinstance(k.value, str)
                                        for k in child.value.keys)):
                            dict_key_types.setdefault(target.id, "string")
            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name) and child.target.id not in shared:
                    scope[child.target.id] = (
                        self._m5_get_type_name(child.annotation, _scope_name)
                        if child.annotation else "Any"
                    )
                    if child.annotation is not None:
                        nu = self._m5_get_dict_value_type(child.annotation)
                        if nu is not None:
                            dict_value_types[child.target.id] = nu
                        kappa = self._m5_get_dict_key_type(child.annotation)
                        if kappa is not None:
                            dict_key_types[child.target.id] = kappa
            elif isinstance(child, ast.For):
                if isinstance(child.target, ast.Name) and child.target.id not in shared:
                    scope[child.target.id] = "Any"
                elif isinstance(child.target, ast.Tuple):
                    for elt in child.target.elts:
                        if isinstance(elt, ast.Name) and elt.id not in shared:
                            scope[elt.id] = "Any"

        # cleared-hash.md S1(b): USAGE-based κ inference. A dict local written or
        # read with a STRING key (`d[k] = v`, `d[k]`, `k in d`, `d.get(k)` where `k`
        # is a string literal or a `str`-typed name) is string-keyed → `map string
        # (option ν)`, native equality, no `str_hash_op`. Python dicts are
        # homogeneously keyed, so any string-key evidence pins κ = string soundly;
        # a dict used only with int keys is never tagged (stays `map int`). This
        # subsumes the un-annotated `d = {}` local that today emits the opaque
        # `str_hash_op` (a bodyless `val` illegal in the resulting VC formula).
        # Does not override an explicit `Dict[str, _]` annotation or the literal
        # signal above (setdefault). Only fires for names bound in `scope` (a
        # dict local/param of THIS function), never shared module vars.
        _str_typed = {n for n, t in scope.items() if t == "str"}

        def _is_str_key(_k: ast.expr) -> bool:
            if isinstance(_k, ast.Constant) and isinstance(_k.value, str):
                return True
            if isinstance(_k, ast.Name) and _k.id in _str_typed:
                return True
            if isinstance(_k, ast.JoinedStr):  # f-string key
                return True
            return False

        def _tag_str_keyed(_name: str) -> None:
            if _name in scope and _name not in shared:
                dict_key_types.setdefault(_name, "string")

        for child in ast.walk(node):
            # d[k]  (subscript read OR the target of `d[k] = v`)
            if (isinstance(child, ast.Subscript)
                    and isinstance(child.value, ast.Name)):
                _idx = child.slice
                if type(_idx).__name__ == "Index":  # py<3.9 compat
                    _idx = _idx.value
                if _is_str_key(_idx):
                    _tag_str_keyed(child.value.id)
            # k in d  /  k not in d
            elif isinstance(child, ast.Compare) and len(child.ops) == 1 \
                    and isinstance(child.ops[0], (ast.In, ast.NotIn)):
                _rhs = child.comparators[0]
                if isinstance(_rhs, ast.Name) and _is_str_key(child.left):
                    _tag_str_keyed(_rhs.id)
            # d.get(k[, default])  /  s.add(k) / s.discard(k) / s.remove(k)
            elif (isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr in ("get", "add", "discard", "remove")
                    and isinstance(child.func.value, ast.Name)
                    and child.args and _is_str_key(child.args[0])):
                # `.add`/`.discard`/`.remove` with a string element pins a SET local's
                # κ = string (a set shares the dict `map` model; its element is the key),
                # so the set-add write and membership read agree on native string keys.
                _tag_str_keyed(child.func.value.id)

        # Ghost variables — register all declarations. Only op == "=" declarations
        # carry a meaningful declared_type; augmented assignments must not overwrite
        # a type already registered. (Module4's second/validation pass is purely a
        # check and writes nothing to the scope, so it is not reproduced here.)
        for child in ast.walk(node):
            for ga in getattr(child, 'csl_ghost_assigns', []):
                if isinstance(ga, GhostArraySetDecl):
                    continue  # element-set: no declared_type; array var already registered
                dtype = getattr(ga, 'declared_type', 'int')
                if ga.target not in scope or ga.op == "=":
                    scope[ga.target] = dtype

        return scope, dict_value_types, dict_key_types, param_annotations, param_list_elem_types

    def _build_function_ir(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Build the core function IR dict (name, contracts, body)."""
        func_name = (f"{self._current_class.lower()}__{node.name}"
                     if self._current_class else node.name)
        # typing-engagement ty1 / 26-0000-typing-spec-2: reset the per-function
        # Literal accumulators BEFORE building the symbol table (which calls
        # `_m5_get_type_name` on each param annotation and may synthesize
        # `requires` clauses into `_cur_literal_requires`). The return-annotation
        # path below may additionally synthesize `ensures` clauses into
        # `_cur_literal_ensures`. Both are flushed into `contracts` at the end.
        self._cur_literal_requires = []
        self._cur_literal_ensures = []
        # refactor.md B-final wedge: Module5 computes the scope itself rather than
        # copying Module4's `node.csl_symbol_table` (etc.). Byte-identical by design.
        _sym, _dvt, _dkt, _pann, _plet = self._build_function_symbol_table(node)
        symbol_table = {k: v for k, v in _sym.items() if k != 'self'}
        # scc3.md Phase B: expose this function's symbol table to `_csl_in` (built
        # below for contracts/body) so `x in S` dispatches on the collection type.
        self._cur_func_symtab = symbol_table
        # STEP 1 (B-final): surface name for the \proj-index guard in `_csl_proj`.
        self._cur_func_name = f"function '{node.name}'"
        return_annotation = None
        return_value_type = None
        is_noreturn = False
        if node.returns:
            if isinstance(node.returns, ast.Name):
                if node.returns.id == "NoReturn":
                    # typing-engagement ty1 / 28-0000-typing-spec-4 §1.0 NR1:
                    # `-> NoReturn` (PEP 484) — the function never returns
                    # normally. Record the IR flag (consumed by Module 6 to emit
                    # `ensures { false }` and by the non-vacuity gate's NR4
                    # exemption). The return_annotation stays None (no return
                    # value type — the body never reaches a normal exit).
                    is_noreturn = True
                    return_annotation = None
                else:
                    return_annotation = node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return_annotation = str(node.returns.value)
            elif isinstance(node.returns, ast.BinOp) and isinstance(node.returns.op, ast.BitOr):
                # PEP 604 `X | Y` return — route through Union normalization.
                return_annotation = self._normalize_union_annotation(
                    node.returns, node.name)
            elif isinstance(node.returns, ast.Subscript):
                # Parametric annotations like `List[str]`, `Tuple[int, int]`,
                # `Dict[str, Any]`, `Optional[int]`. Capture the head identifier
                # (lower-cased so `List` → `list` matches Module6's existing
                # case-sensitive checks against the bare `list` annotation).
                if isinstance(node.returns.value, ast.Name):
                    head = node.returns.value.id
                    if head == "Literal":
                        # `-> Literal[v1, ..., vn]` — synthesize a ground
                        # `ensures \result == v1 \/ ...` clause (typing-engagement
                        # ty1 / 26-0000-typing-spec-2 §1.3 step 6). The base type
                        # is the return type. `_normalize_literal_annotation`
                        # appends to `self._cur_literal_ensures`.
                        return_annotation = self._normalize_literal_annotation(
                            node.returns, "\\result")
                    elif head in ("Optional", "Union"):
                        # `Optional[T]` / `Union[...]` return — synthesize a
                        # per-site variant (typing-engagement ty1), so the
                        # return type is a real sum type, not a collapsed int.
                        return_annotation = self._normalize_union_annotation(
                            node.returns, node.name)
                    else:
                        return_annotation = head.lower()
                        # item34.md CF5: capture a `List[str]`/`List[int]` return's ELEMENT
                        # type (mirrors the param path `_m5_get_list_elem_type`) so Module6
                        # lowers `-> List[str]` to `array string` (the `_callee_raised_*`
                        # name-list stubs), not the default `array int`.
                        if head in ("List", "list"):
                            return_value_type = self._m5_get_list_elem_type(node.returns)
            elif isinstance(node.returns, ast.Attribute):
                # `typing.NoReturn` (Attribute value=Name "typing", attr
                # "NoReturn") — the qualified spelling of the PEP 484 marker.
                # Treated identically to the bare `-> NoReturn` form (NR1).
                # Other Attribute returns fall through (return_annotation stays
                # None — the original behaviour for unrecognised forms).
                if (node.returns.attr == "NoReturn"
                        and isinstance(node.returns.value, ast.Name)
                        and node.returns.value.id == "typing"):
                    is_noreturn = True
                    return_annotation = None
        # Fallback: a bare Name/Constant that we didn't recognise above.
        # Formal parameter names ONLY (excluding `self`). Distinct from
        # `symbol_table`, which Module4 also populates with local
        # variables, for-loop targets, and ghost vars. Module6's
        # parameter-mutation handling needs the unpolluted list to
        # decide which pre_decl_vars should be shadowed via
        # `let X = ref X in` (formal params) vs `let X = ref 0 in`
        # (other locals).
        formal_params = [a.arg for a in node.args.args if a.arg != 'self']
        # 1111-spec R7: positional default values (param name -> default IR), so a
        # cross-module call passing fewer args than the callee arity can fill the
        # missing trailing params from these defaults at the call site.
        param_defaults: Dict[str, Any] = {}
        _pos_args = node.args.args
        _defs = node.args.defaults
        if _defs:
            for _a, _d in zip(_pos_args[len(_pos_args) - len(_defs):], _defs):
                if _a.arg != 'self':
                    param_defaults[_a.arg] = self._py_expr_to_ir(_d)
        # Front-end resolution of a Python-specific fact for the core's no-mutable-default
        # check (refactor.md AST-only #3): is any default arg mutable — a list/dict/set
        # literal, or a list()/dict()/set() call — over ALL defaults (positional + keyword
        # only, the latter being the gap `param_defaults` misses). The core
        # (core_ir_semantic._check_mutable_defaults) raises the language-agnostic error.
        _all_defaults = list(getattr(node.args, "defaults", []) or []) + [
            _d for _d in (getattr(node.args, "kw_defaults", []) or []) if _d is not None]
        has_mutable_default = any(
            isinstance(_d, (ast.List, ast.Dict, ast.Set)) or
            (isinstance(_d, ast.Call) and isinstance(_d.func, ast.Name)
             and _d.func.id in ("list", "dict", "set"))
            for _d in _all_defaults)
        # Plumb the PRE-DESUGAR acts (Module3 stashes them on node.csl_acts before
        # desugaring to requires/ensures) for the core's act-specific validation
        # (core_ir_semantic._check_acts; refactor.md AST-only #3). Metadata only — the
        # desugared requires/ensures (consumed by Module6) are unchanged, so emission
        # is byte-identical. Each Act carries its `given` guard exprs (for the
        # \result-in-guard check); Complete/Disjoint carry their referenced names.
        acts_ir = []
        for _a in getattr(node, "csl_acts", []) or []:
            if isinstance(_a, Act):
                acts_ir.append({
                    "kind": "act", "name": _a.name,
                    "given_exprs": [self._csl_to_ir(_cl.expr)
                                    for _cl in _a.clauses if isinstance(_cl, Given)],
                })
            elif isinstance(_a, Complete):
                acts_ir.append({"kind": "complete", "names": list(_a.names)})
            elif isinstance(_a, Disjoint):
                acts_ir.append({"kind": "disjoint", "names": list(_a.names)})
        return {
            "name": func_name,
            "symbol_table": symbol_table,
            "param_annotations": _pann,
            "param_list_elem_types": dict(_plet),
            "param_defaults": param_defaults,
            "has_mutable_default": has_mutable_default,
            "acts": acts_ir,
            # no-more-int-3 A1: dict var -> WhyML value type ν (string), for
            # string-valued dicts only (captured in Module4); int-valued dicts
            # have no entry and keep the `map int (option int)` path.
            "dict_value_types": dict(_dvt),
            "dict_key_types": dict(_dkt),
            "formal_params": formal_params,
            "return_annotation": return_annotation,
            "return_value_type": return_value_type,
            # typing-engagement ty1 / 28-0000-typing-spec-4: `-> NoReturn` (PEP
            # 484) sets the IR flag consumed by Module 6 (`ensures { false }`,
            # NR1) and the non-vacuity gate (NR4 exemption). Emitted ONLY when
            # true → byte-identical for every non-NoReturn driver (additive IR
            # v1.3 field; see docs/ir.md §5/§10).
            **({"is_noreturn": True} if is_noreturn else {}),
            # typing-engagement ty3 / 33-1700-typing-spec-9: PEP 695 type
            # parameters of a generic top-level function (`def f[T]():`). Methods
            # of a generic class carry the class's type_params via the
            # monomorphization pass (which substitutes the class's TypeVar in
            # its methods). ABSENT on non-generic functions (emitted only when
            # non-empty → byte-identical for unaffected drivers, additive IR v1.4).
            **({"type_params": self._collect_type_params(node)}
               if getattr(node, "type_params", None) else {}),
            "contracts": {
                # typing-engagement ty1 / 26-0000-typing-spec-2: merge the
                # synthesized Literal `requires`/`ensures` clauses AFTER the
                # user-written `csl_requires`/`csl_ensures` (order within
                # requires/ensures is logically conjunctive and commutative, so
                # this is a rendering detail only). The accumulators are empty
                # for non-Literal functions → byte-identical emission.
                "requires": (self._csl_list_to_ir(getattr(node, 'csl_requires', []))
                             + list(self._cur_literal_requires)),
                "ensures": (self._csl_list_to_ir(getattr(node, 'csl_ensures', []))
                            + list(self._cur_literal_ensures)),
                "assigns": [self._csl_to_ir(t) for a in getattr(node, 'csl_assigns', []) for t in a.targets],
                "raises": [{"exc_type": r.exc_type, "condition": self._csl_to_ir(r.condition)}
                           for r in getattr(node, 'csl_raises', [])],
                # `no_exception E1, E2, ...` — list of exception names the
                # function commits to not raising. Phase 1 of the
                # NoException workplan; see exception_model.py for the
                # trigger table.
                "no_exception": list(getattr(node, 'csl_no_exception', []) or []),
                "no_exception_all": bool(getattr(node, 'csl_no_exception_all', False)),
            },
            "body": self._py_stmts_to_ir(node.body),
            "function_variants": self._csl_list_to_ir(getattr(node, 'csl_function_variants', [])),
            "diverges": getattr(node, 'csl_diverges', False),
            "no_inline": getattr(node, 'csl_no_inline', False),
            "sibling_concrete": getattr(node, 'csl_sibling_concrete', False),
            # module-emission.md: opt-in axiom-isolation group name ("" = flat default).
            "verify_module": getattr(node, 'csl_verify_module', "") or "",
            "propagate_frame": getattr(node, 'csl_propagate_frame', False),
            "fresh_globals": getattr(node, 'csl_fresh_globals', False),
            "trusted": getattr(node, 'csl_trusted', False),
            "abstract": getattr(node, 'csl_abstract', False),
            # 07-1143 R4: `#@ \preserves` opt-in (HAPPY trust boundary), surfaced in the
            # IR so `--soundness-report` can classify the function as Confinement-trusted.
            "preserves": getattr(node, 'csl_preserves', False),
            "lemma": getattr(node, 'csl_lemma', False),
            "uses": list(getattr(node, 'csl_uses', []) or []),
            # b-spec Track B: the NARROW interface contract importers see (opacity). Absent (empty
            # dict) ⇒ interface = definition (transparent — every existing function byte-identical).
            "interface": (
                {
                    "requires": self._csl_list_to_ir(getattr(node, 'csl_iface_requires', [])),
                    "ensures": self._csl_list_to_ir(getattr(node, 'csl_iface_ensures', [])),
                    "assigns": [self._csl_to_ir(t) for a in getattr(node, 'csl_iface_assigns', []) for t in a.targets],
                }
                if (getattr(node, 'csl_iface_ensures', []) or getattr(node, 'csl_iface_requires', [])
                    or getattr(node, 'csl_iface_assigns', []))
                else {}
            ),
            "reveal": list(getattr(node, 'csl_reveal', []) or []),
            # no-more-int Stage F: a memoizing decorator requires a referentially
            # transparent function (checked in _check_memoization_soundness).
            "memoized": self._is_memoized(node),
            "reviewer": getattr(node, 'csl_reviewer', ""),
            "bounded_int": getattr(node, 'csl_bounded_int', None),
            # §2.1.12 — proof citations from cross-validated Rocq+Lean
            # theorems. Module6 emits a Why3 `axiom` block in the
            # preamble for each entry; see docs/cross-validated-spec-sources.md.
            "proof": [
                {"prover": a.prover, "qualname": a.qualname}
                for a in getattr(node, 'csl_proof', [])
            ],
            # Mixin composition (Tier 1). `provides` lists the method names this
            # method is a provider for; `method_deps` are the declared
            # depends_method/requires_method interfaces (with their own contracts)
            # this method may call via `self.<m>(…)`. Module6 emits each dep as an
            # abstract `val` carrying its `ensures` so the provider verifies once
            # against it (S1); the Module4 composition pass (S2) discharges
            # provider ⊑ dependency. Empty for non-mixin methods → no effect.
            "provides": list(getattr(node, 'csl_provides', []) or []),
            "method_deps": [
                {"method": d["method"], "sig": d["sig"], "kind": d["kind"],
                 "requires": self._csl_list_to_ir(d["requires"]),
                 "ensures": self._csl_list_to_ir(d["ensures"])}
                for d in getattr(node, 'csl_method_deps', []) or []
            ],
            # Field classification (D1): names this mixin method declared it may touch.
            "shared_state": [{"name": s.name, "type": s.type_str}
                             for s in getattr(node, 'csl_mixin_shared_state', []) or []],
            "touches_field": [{"name": s.name, "type": s.type_str}
                              for s in getattr(node, 'csl_touches_field', []) or []],
        }

    def _detect_array_dimensions(self, func_ir: Dict[str, Any]) -> None:
        """Detect 2D and 1D array params from contracts and body access patterns."""
        symbol_table = func_ir["symbol_table"]
        # 0442.md B2 (no-more-int): `bytes`/`bytearray` are the byte-buffer array
        # class (`array int`), so they are 1-D array param candidates like `list`.
        candidate_params = {k for k, v in symbol_table.items()
                            if v in ("list", "Any", "bytes", "bytearray")}
        array2d: Set[str] = set()
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Length2D":
                base = req.get("base")
                if base in candidate_params:
                    array2d.add(base)
        if candidate_params:
            array2d.update(self._collect_2d_params(func_ir["body"], candidate_params))
        if array2d:
            func_ir["array2d_params"] = sorted(array2d)
        array1d: Set[str] = set()
        for req in func_ir["contracts"]["requires"]:
            if isinstance(req, dict) and req.get("type") == "Valid":
                base = req.get("base")
                if base and base in candidate_params and base not in array2d:
                    array1d.add(base)
        # 07-1321 S4: a list/bytes/bytearray candidate that is the target of `+=`
        # (Python list/bytes extension → array concatenation) is array-typed too, even
        # without a `\valid` requires — otherwise `dst += src` mis-lowers to integer
        # `+` (an `array int` vs `int` type error). Routing it here sends it to the
        # array-extend path in `_handle_augassign_stmt`. (Faithful length-additive
        # concatenation is a documented follow-on; this removes the type error.)
        # Restrict to params DEFINITELY array-typed (`list`/`bytes`/`bytearray`),
        # excluding `Any`: an `Any`-typed int accumulator (`total += 1`) is also a `+=`
        # target and must NOT be reclassified as an array (that was the bug the `\valid`
        # gate guarded against).
        strict_array_cands = {k for k, v in symbol_table.items()
                              if v in ("list", "bytes", "bytearray")}

        def _collect_augextend(node, out):
            if isinstance(node, dict):
                if (node.get("stmt") == "AugAssign" and node.get("op") == "+"
                        and node.get("target") in strict_array_cands):
                    out.add(node["target"])
                for v in node.values():
                    _collect_augextend(v, out)
            elif isinstance(node, list):
                for x in node:
                    _collect_augextend(x, out)
        aug_ext: Set[str] = set()
        _collect_augextend(func_ir["body"], aug_ext)
        array1d |= (aug_ext - array2d)
        if array1d:
            func_ir["array1d_params"] = sorted(array1d)

    @staticmethod
    def _is_decode_call(ir: Any) -> bool:
        """str-list-elements: is `ir` a `bytes.decode(...)` call (the `func` tail is
        `decode`)? `b.decode()` lowers to a `Call` whose `func` is `"decode"` (receiver
        a Subscript) or `"<name>.decode"` (receiver a Name). Its result is a `str`."""
        if not isinstance(ir, dict) or ir.get("type") != "Call":
            return False
        fn = ir.get("func")
        return isinstance(fn, str) and (fn == "decode" or fn.endswith(".decode"))

    def _collect_str_decode_locals(self, body: Any) -> Set[str]:
        """str-list-elements: locals assigned a `.decode()` result — these are `str`."""
        out: Set[str] = set()

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign" and isinstance(node.get("target"), str):
                    if self._is_decode_call(node.get("value")):
                        out.add(node["target"])
                for v in node.values():
                    rec(v)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(body)
        return out

    def _detect_seq_promotion(self, func_ir: Dict[str, Any]) -> None:
        """07-1705-rev4 P2 — the seq-promotion analysis (diagnostics only; no emission
        change). A `list`/`bytes`/`bytearray` variable is **seq-promoted** (must be
        modelled as `seq int`, a growable immutable value in a region-free ref) iff it is
        ever GROWN: the target of `+=` with a list RHS, or assigned `a + b` on lists. The
        mark propagates across `b = a` (representation must unify). A seq-promoted var
        that is also used in a 2-D context is a representation CONFLICT (rev4 §7) — a
        list cannot be both growable-seq and 2-D-array. Results are stored as IR metadata
        (`seq_promoted_vars`, `seq_promotion_conflicts`) for P3's lowering to consume;
        until P3 lands, the keys are inert and emission is byte-identical."""
        symbol_table = func_ir.get("symbol_table", {})
        list_vars = {k for k, v in symbol_table.items()
                     if v in ("list", "bytes", "bytearray")}
        # Locals assigned a list literal or a list-producing call are list-typed too
        # (the symbol table types them `Any`). Pre-pass to seed those.
        def _seed_list_vars(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Assign":
                    val = node.get("value", {})
                    if isinstance(val, dict):
                        if val.get("type") == "ArrayLit":
                            list_vars.add(node.get("target"))
                        elif (val.get("type") == "Call"
                              and val.get("func") in ("list", "sorted", "bytes", "bytearray")):
                            list_vars.add(node.get("target"))
                for v in node.values():
                    _seed_list_vars(v)
            elif isinstance(node, list):
                for x in node:
                    _seed_list_vars(x)
        _seed_list_vars(func_ir["body"])
        list_vars.discard(None)
        if not list_vars:
            return
        grown: Set[str] = set()
        index_set: Set[str] = set()         # vars that are index-ASSIGNED (`x[i] = v`)
        edges: List[Tuple[str, str]] = []   # (target, source) for `b = a` unification
        # str-list-elements: per-seq-var the IRs of the elements appended/concatenated
        # into it. A seq whose elements are ALL string-producing (a `.decode()` result
        # or a string literal/local) is typed `seq string`, not the default `seq int`.
        append_elems: Dict[str, List[Any]] = {}

        def _record_elem(tgt: str, elem: Any) -> None:
            append_elems.setdefault(tgt, []).append(elem)

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                st = node.get("stmt")
                if (st == "AugAssign" and node.get("op") == "+"
                        and node.get("target") in list_vars):
                    grown.add(node["target"])
                elif st == "ArraySet" and node.get("target") in list_vars:
                    # return-arr.md follow-on: a list that is index-MUTATED (`x[i] = v`)
                    # CANNOT be an immutable seq — it must stay an array-local. Exclude it
                    # (and anything unified with it) from seq promotion below.
                    index_set.add(node["target"])
                elif (st == "Expr" and isinstance(node.get("value"), dict)
                      and node["value"].get("type") == "Call"
                      and isinstance(node["value"].get("func"), str)
                      and node["value"]["func"].endswith(".append")):
                    # return-arr.md follow-on: `.append()` GROWS a list (was previously only
                    # `+=`/`a+b`). Recognising it lets append-built-then-returned lists become
                    # seq, so `len`/`\length` track the logical length (not the 1024-backing).
                    tgt = node["value"]["func"].rsplit(".", 1)[0]
                    if tgt in list_vars:
                        grown.add(tgt)
                        _args = node["value"].get("args", [])
                        if _args:
                            _record_elem(tgt, _args[0])
                elif st == "Assign":
                    tgt = node.get("target")
                    val = node.get("value", {})
                    if isinstance(val, dict):
                        if (val.get("type") == "BinOp" and val.get("op") == "+"
                                and tgt in list_vars):
                            for side in ("left", "right"):
                                s = val.get(side, {})
                                if (isinstance(s, dict) and s.get("type") == "Var"
                                        and s.get("name") in list_vars):
                                    grown.add(tgt)
                        if (val.get("type") == "Var" and tgt in list_vars
                                and val.get("name") in list_vars):
                            edges.append((tgt, val["name"]))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for x in node:
                    walk(x)
        walk(func_ir["body"])

        # Unify representation across `b = a` edges: growth (or index-set) on either end ⇒ both.
        seq = set(grown)
        blocked = set(index_set)
        changed = True
        while changed:
            changed = False
            for t, s in edges:
                if (s in seq) != (t in seq):
                    seq.add(s); seq.add(t); changed = True
                if (s in blocked) != (t in blocked):
                    blocked.add(s); blocked.add(t); changed = True
        # An index-mutated list can't be a seq — drop it (and its unified partners).
        seq -= blocked

        if seq:
            func_ir["seq_promoted_vars"] = sorted(seq)
            # rev4 §7: a growable list cannot also be a 2-D array — flag the conflict.
            conflicts = seq & set(func_ir.get("array2d_params", []))
            if conflicts:
                func_ir["seq_promotion_conflicts"] = sorted(conflicts)
            # str-list-elements: type a seq whose appended elements are ALL strings as
            # `seq string`. Default stays `seq int` (no entry), so int-element lists are
            # byte-identical. A seq carries STRING elements iff every appended element is
            # string-producing — a string literal, a `.decode()`-assigned local, or a var
            # already unified (via `b = a`) with such a seq.
            symbol_table = func_ir.get("symbol_table", {})
            str_locals = self._collect_str_decode_locals(func_ir["body"])

            def _is_str_elem(elem: Any) -> bool:
                if not isinstance(elem, dict):
                    return False
                t = elem.get("type")
                if t == "String":
                    return True
                if t == "Var":
                    nm = elem.get("name")
                    return nm in str_locals or symbol_table.get(nm) in ("str", "string")
                if t == "Call" and self._is_decode_call(elem):
                    return True
                return False

            seq_value_types: Dict[str, str] = {}
            for v in seq:
                elems = append_elems.get(v, [])
                if elems and all(_is_str_elem(e) for e in elems):
                    seq_value_types[v] = "string"
            # Propagate string-ness across `b = a` unification edges (both directions),
            # so a seq aliased to a string seq is also `seq string`.
            changed = True
            while changed:
                changed = False
                for t, s in edges:
                    if t in seq and s in seq:
                        if (seq_value_types.get(t) == "string") != (seq_value_types.get(s) == "string"):
                            seq_value_types[t] = "string"
                            seq_value_types[s] = "string"
                            changed = True
            if seq_value_types:
                func_ir["seq_value_types"] = dict(seq_value_types)
                # Mark the decode-assigned string locals (e.g. `name`) as `str` in the
                # symbol table so Module6 lets-binds them as a string ref (not `ref 0`),
                # making the `Seq.snoc !names string` element well-typed.
                for v in str_locals:
                    if symbol_table.get(v) in (None, "Any"):
                        symbol_table[v] = "str"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self._should_skip_method(node):
            return
        # typing-engagement ty2 / 31-1700-typing-spec-7 §1.3: an `@overload`
        # stub (`@overload def f(x: T) -> R: ...`) is collected into
        # `_pending_overloads[name]` as a guarded postcondition
        # `isinstance(p_i, T_i) ==> Q_i` (O2/O3) and is NOT emitted as a function
        # IR node — its body is `...`/`pass` (R1, discarded at runtime). The
        # guarded postconditions are appended to the implementation's ensures when
        # the non-`@overload` `def f(...)` is visited below (O6). Byte-identical
        # for non-overload drivers: the check is a pure decorator-name + body-
        # shape test.
        if self._is_overload_stub(node):
            guarded = self._synthesize_overload_guard(node)
            if guarded:
                self._pending_overloads.setdefault(node.name, []).extend(guarded)
            return
        func_ir = self._build_function_ir(node)
        # typing-engagement ty2 / 31-1700-typing-spec-7 §1.3 step 3: attach the
        # collected guarded postconditions to the implementation's ensures (O6).
        # Appended AFTER `_build_function_ir` (which already merged user-written
        # + Literal ensures); order within ensures is conjunctive/commutative.
        if node.name in self._pending_overloads:
            func_ir["contracts"]["ensures"].extend(
                self._pending_overloads.pop(node.name))
        # §4.4 source span — the IR carries the function's location so the core can
        # report IR-level (migrated) semantic errors against the original source.
        # The prerequisite for re-pointing semantic analysis off the AST onto the IR
        # (refactor.md Phase B). Module6 ignores these metadata keys (emission unchanged).
        func_ir["line"] = getattr(node, "lineno", 0)
        func_ir["col"] = getattr(node, "col_offset", 0)
        self._detect_purity(func_ir)
        self._check_memoization_soundness(func_ir)
        self._detect_array_dimensions(func_ir)
        self._detect_seq_promotion(func_ir)   # 07-1705-rev4 P2 (diagnostics-only metadata)
        if getattr(node, 'csl_thread_entry', False):
            func_ir["thread_entry"] = True
            if "thread_entries" not in self.program_ir:
                self.program_ir["thread_entries"] = []
            self.program_ir["thread_entries"].append(func_ir["name"])
        if self._current_class:
            func_ir["kind"] = "method"
            func_ir["self_type"] = self._current_class
        self.program_ir["functions"].append(func_ir)
        self.generic_visit(node)

    # typing-engagement ty2 / 31-1700-typing-spec-7 — @overload (PEP 484) helpers.
    # The static plane treats an @overload family as a guarded contract family
    # (O1–O6): each stub's postcondition is guarded by its parameter-type
    # predicate; the single implementation proves each guarded postcondition.
    # The runtime plane discards stubs (R1) — see src/pycsl_lib/typ shim. NO-BLEND
    # (D1): the guard is a WhyML formula over the parameter's type tag (a type
    # judgment), NOT the runtime isinstance dispatch (a value check).

    @staticmethod
    def _is_overload_stub(node: ast.FunctionDef) -> bool:
        """True iff `node` is an `@overload` stub: it carries an `@overload`
        decorator (bare `Name("overload")` or `Attribute(attr="overload")`) AND
        its body is exactly the literal `...` (Ellipsis) or `pass` (O1a — a stub
        carries no executable code; a non-`...` body is a regular decorated
        function, byte-identical fallback)."""
        has_overload = False
        for d in node.decorator_list:
            if isinstance(d, ast.Name) and d.id == "overload":
                has_overload = True
                break
            if isinstance(d, ast.Attribute) and d.attr == "overload":
                has_overload = True
                break
        if not has_overload:
            return False
        body = node.body
        if len(body) != 1:
            return False
        stmt = body[0]
        if isinstance(stmt, ast.Pass):
            return True
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis):
            return True
        return False

    def _synthesize_overload_guard(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Synthesize the guarded postconditions for one `@overload` stub (O2/O3).
        For each parameter `p_i: T_i`, the guard is `isinstance(p_i, T_i)` (the
        same predicate vocabulary the body-level isinstance lowering uses —
        `_handle_isinstance` at expressions.py:2024 emits `(subtag <typeof p_i>
        <T_i tag>)`, a WhyML bool). For each `#@ ensures Q_i` on the stub, the
        guarded postcondition `isinstance(p_i, T_i) ==> Q_i` is built (the `==>`
        operator is parsed by Module2_Parser IMPL_OP and lowered to WhyML `->`).
        A stub with no `#@ ensures` returns `[]` (O3 — the guard is still
        synthesized for selection but contributes no VC)."""
        guard = self._build_overload_param_guard(node)
        if guard is None:
            return []
        clauses: List[Dict[str, Any]] = []
        for csl_ens in getattr(node, 'csl_ensures', []) or []:
            q_ir = self._csl_to_ir(csl_ens.expr)
            clauses.append({
                "type": "BinOp", "op": "==>",
                "left": guard, "right": q_ir,
            })
        return clauses

    def _build_overload_param_guard(self, node: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        """Build the conjunction of per-parameter `isinstance(p_i, T_i)` guards
        for the stub. For the monomorphic TY2 scope each stub has exactly one
        typed parameter, so the guard is the single isinstance call. Returns
        None if no parameter carries a type annotation (no guard → no guarded
        postcondition)."""
        guards: List[Dict[str, Any]] = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            ann = arg.annotation
            if ann is None:
                continue
            t_name = self._overload_type_name(ann)
            if t_name is None:
                continue
            guards.append({
                "type": "Call", "func": "isinstance",
                "args": [{"type": "Var", "name": arg.arg},
                         {"type": "Var", "name": t_name}],
            })
        if not guards:
            return None
        if len(guards) == 1:
            return guards[0]
        acc = guards[0]
        for g in guards[1:]:
            acc = {"type": "BinOp", "op": "and", "left": acc, "right": g}
        return acc

    @staticmethod
    def _overload_type_name(ann: ast.AST) -> Optional[str]:
        """Resolve a parameter annotation to its type-name string for the guard.
        A `Name` → `id`; an `Attribute` → `attr` (so `typing.int`-style spellings
        resolve). Lower-cased to match the existing int/str/bool/bytes/float
        vocabulary the isinstance lowering's `_tag_of_type` expects."""
        if isinstance(ann, ast.Name):
            return ann.id.lower()
        if isinstance(ann, ast.Attribute):
            return ann.attr.lower()
        return None

class Module5_IREmitter:
    """Consumes the validated AAST and outputs a JSON string."""
    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree

    def generate_json(self, indent: int = 2) -> str:
        emitter = PyCSLToJSONEmitter()
        emitter.visit(self.tree)
        return json.dumps(emitter.program_ir, indent=indent)
