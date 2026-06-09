from __future__ import annotations

import warnings
import pure_ast as ast  # consume the same pure-Python tree Module3 builds
from typing import Callable, Dict, List, Optional, Set, Any
from Module2_Parser import (
    CSLNode, ContractWrapper, QuantifierNode, SingleExprNode,
    Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    Var, Result, Old, BinOp, UnaryOp, Nothing, Number, FieldAccess,
    ClassInvariant, Forall, Exists, ForallItems, ArrayLength, SubscriptAccess,
    AssignsRegion, Valid, Separated, FunctionVariant,
    SharedDecl, MutexInvariant, LockOrder, ChainedSubscript,
    GhostAssignDecl, GhostArraySetDecl,
    # ghost-tuple nodes
    MkTupleExpr, FstExpr, SndExpr, ProjExpr,
    # ghost-string nodes
    StrConcatExpr, StrLengthExpr, StrSubExpr,
    # ghost-array nodes
    GhostCopyExpr, GhostCopyRangeExpr, GhostMakeExpr,
    # ghost-dict nodes
    MapEmptyExpr, MapGetExpr, MapSetExpr, MapEqExpr, HasKeyExpr, MapRemoveExpr,
    # ghost-set nodes
    SetEmptyExpr, SetAddExpr, SetRemoveExpr, SetMemExpr,
    SetUnionExpr, SetInterExpr, SetDiffExpr, SetCardExpr,
    SetSubsetExpr, SetEqExpr,
    # ghost-list nodes
    NilExpr, ConsExpr, HdExpr, TlExpr, ListLengthExpr,
    NthExpr, MemExpr, AppendExpr,
)
from errors import PyCSLSemanticError


def _module_const_int(value: Any) -> Optional[int]:
    """Int value of an int-literal expr (incl. unary `-N`), else None. Mirrors
    `Module5._const_int_value`."""
    if (isinstance(value, ast.Constant) and isinstance(value.value, int)
            and not isinstance(value.value, bool)):
        return int(value.value)
    if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
            and isinstance(value.operand, ast.Constant)
            and isinstance(value.operand.value, int)
            and not isinstance(value.operand.value, bool)):
        return -int(value.operand.value)
    return None


def collect_module_constants(node: ast.Module) -> Dict[str, int]:
    """Module-level integer constants: a top-level `NAME = <int literal>` (or annotated)
    bound EXACTLY ONCE at module scope, that is not a `#@ shared` global and is never
    written via `global`. These are safe to inline as literals in contracts and bodies
    (mirrors class-body constants, `Module5._collect_class_constants`). A reassigned name
    is mutable global state and is excluded — contracts cannot soundly reference it in the
    per-function frame model (see module-constants-plan.md Q2). Shared between Module4
    (contract-scope validation) and Module5 (IR emission)."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, int] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        iv = _module_const_int(value)
        if iv is not None:
            candidates[target] = iv
        # 0442.md C5 (no-more-int): a string-literal module constant folds to a real
        # Why3 `string`, not an int hash. Collected here so contracts may reference it.
        elif isinstance(value, ast.Constant) and isinstance(value.value, str):
            candidates[target] = value.value
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: v for n, v in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


def collect_module_globals(node: ast.Module, class_names: set) -> Dict[str, ast.Call]:
    """inline.md Phase 1 — module-level global OBJECT instances: a top-level
    `g = C(<args>)` where `C` is a class defined in the module, bound EXACTLY ONCE at
    module scope, not a `#@ shared` global and never written via `global`. Returns
    `{name: constructor-Call-ast}`. These are single, named, statically-known objects
    (the simplest aliasing story), modeled as a Why3 mutable-record global; method calls
    on them are inlined (`ir_inline.py`). A reassigned name is excluded (a global
    instance is bound once — see Scope in inline.md). Mirrors `collect_module_constants`."""
    counts: Dict[str, int] = {}
    candidates: Dict[str, ast.Call] = {}
    for child in getattr(node, "body", []):
        target = None
        value = None
        if (isinstance(child, ast.Assign) and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)):
            target, value = child.targets[0].id, child.value
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            target, value = child.target.id, child.value
        if target is None:
            continue
        counts[target] = counts.get(target, 0) + 1
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id in class_names):
            candidates[target] = value
    shared = {d.variable for d in getattr(node, "csl_shared_decls", [])}
    written_via_global = {n for g in ast.walk(node) if isinstance(g, ast.Global)
                          for n in g.names}
    return {n: c for n, c in candidates.items()
            if counts.get(n, 0) == 1 and n not in shared
            and n not in written_via_global}


# ---------------------------------------------------------
# 2. Generic CSL Tree Utilities
# ---------------------------------------------------------

_CSL_CHILDREN_MAP: Dict[type, Callable[[CSLNode], List[CSLNode]]] = {
    BinOp:          lambda n: [n.left, n.right],
    UnaryOp:        lambda n: [n.expr],
    Old:            lambda n: [n.expr],
    Requires:       lambda n: [n.expr],
    Ensures:        lambda n: [n.expr],
    LoopInvariant:  lambda n: [n.expr],
    LoopVariant:    lambda n: [n.expr],
    ClassInvariant: lambda n: [n.expr],
    FunctionVariant: lambda n: [n.expr],
    Forall:         lambda n: [n.body],
    Exists:         lambda n: [n.body],
    Assigns:        lambda n: list(n.targets),
    SubscriptAccess: lambda n: [n.index],
    ChainedSubscript: lambda n: [n.index1, n.index2],
    AssignsRegion:  lambda n: [n.low, n.high],
    Valid:          lambda n: [n.length],
    Separated:      lambda n: [n.length1, n.length2],
    GhostAssignDecl:    lambda n: [n.value],
    GhostArraySetDecl:  lambda n: [n.index, n.value],
    MkTupleExpr:    lambda n: list(n.elts),
    FstExpr:        lambda n: [n.tuple_expr],
    SndExpr:        lambda n: [n.tuple_expr],
    ProjExpr:       lambda n: [n.tuple_expr, n.index],
    StrConcatExpr:  lambda n: [n.left, n.right],
    StrLengthExpr:  lambda n: [n.string],
    StrSubExpr:     lambda n: [n.string, n.lo, n.hi],
    GhostCopyRangeExpr: lambda n: [n.lo, n.hi],
    GhostMakeExpr:  lambda n: [n.size, n.default],
    MapEmptyExpr:   lambda n: [],
    SetEmptyExpr:   lambda n: [],
    NilExpr:        lambda n: [],
    MapGetExpr:     lambda n: [n.dict_expr, n.key],
    MapSetExpr:     lambda n: [n.dict_expr, n.key, n.value],
    MapEqExpr:      lambda n: [n.left, n.right],
    HasKeyExpr:     lambda n: [n.dict_expr, n.key],
    MapRemoveExpr:  lambda n: [n.dict_expr, n.key],
    SetAddExpr:     lambda n: [n.set_expr, n.elem],
    SetRemoveExpr:  lambda n: [n.set_expr, n.elem],
    SetMemExpr:     lambda n: [n.elem, n.set_expr],
    SetUnionExpr:   lambda n: [n.left, n.right],
    SetInterExpr:   lambda n: [n.left, n.right],
    SetDiffExpr:    lambda n: [n.left, n.right],
    SetSubsetExpr:  lambda n: [n.left, n.right],
    SetEqExpr:      lambda n: [n.left, n.right],
    SetCardExpr:    lambda n: [n.set_expr, n.lo, n.hi],
    ConsExpr:       lambda n: [n.head, n.tail],
    HdExpr:         lambda n: [n.list_expr],
    TlExpr:         lambda n: [n.list_expr],
    ListLengthExpr: lambda n: [n.list_expr],
    NthExpr:        lambda n: [n.list_expr, n.index],
    MemExpr:        lambda n: [n.elem, n.list_expr],
    AppendExpr:     lambda n: [n.left, n.right],
}


def _iter_csl_children(node: CSLNode) -> List[CSLNode]:
    """Return the direct CSL sub-expressions of *node* for structural recursion."""
    handler = _CSL_CHILDREN_MAP.get(type(node))
    if handler:
        return handler(node)
    return []


def _walk_csl_nodes(node: CSLNode):
    """Yield *node* and every CSL sub-node reachable via `_iter_csl_children`."""
    yield node
    for child in _iter_csl_children(node):
        yield from _walk_csl_nodes(child)

# ---------------------------------------------------------
# 3. Contract Variable Extractor
# ---------------------------------------------------------

def extract_variables(node: CSLNode) -> Set[str]:
    """
    Recursively walks a Contract AST node and returns a set of all
    variable names referenced within it.
    FieldAccess nodes (self.field) are excluded — validated separately.
    """
    if isinstance(node, Var):
        return {node.name}
    if isinstance(node, FieldAccess):
        return set()
    if isinstance(node, ArrayLength):
        # `\length(self.f)` references a record field and `\length(\result)`
        # the return value — both excluded here (like FieldAccess / Result),
        # validated structurally rather than against local variable scope.
        if node.var.startswith("self.") or node.var == "\\result":
            return set()
        return {node.var}
    if isinstance(node, GhostCopyExpr):
        return {node.arr}
    if isinstance(node, GhostCopyRangeExpr):
        return {node.arr} | extract_variables(node.lo) | extract_variables(node.hi)
    if isinstance(node, SubscriptAccess):
        base = set() if node.array == "\\result" else {node.array}
        return base | extract_variables(node.index)
    if isinstance(node, ChainedSubscript):
        return {node.array} | extract_variables(node.index1) | extract_variables(node.index2)
    if isinstance(node, AssignsRegion):
        return {node.base} | extract_variables(node.low) | extract_variables(node.high)
    if isinstance(node, Valid):
        return {node.base} | extract_variables(node.length)
    if isinstance(node, Separated):
        return ({node.base1} | extract_variables(node.length1) |
                {node.base2} | extract_variables(node.length2))
    if isinstance(node, ForallItems):
        # 07-1311 Q3: two-binder dict-items quantifier — key/val are bound; coll is free.
        return (extract_variables(node.body) - {node.key, node.val}) | {node.coll}
    if isinstance(node, QuantifierNode):
        return extract_variables(node.body) - {node.var}
    # Generic structural recursion
    result: Set[str] = set()
    for child in _iter_csl_children(node):
        result |= extract_variables(child)
    return result

def contains_result(node: CSLNode) -> bool:
    """Checks if \\result is used anywhere in the expression."""
    if isinstance(node, Result):
        return True
    if isinstance(node, SubscriptAccess) and node.array == "\\result":
        return True
    return any(contains_result(c) for c in _iter_csl_children(node))

# ---------------------------------------------------------
# 3. The Semantic Analyzer (AST Pass)
# ---------------------------------------------------------

class Module4_SemanticAnalyzer(ast.NodeVisitor):
    """
    Walks the Annotated AST (AAST), resolves variable scopes, 
    extracts type hints, and validates contracts against them.
    """
    def __init__(self) -> None:
        self.current_scope: Dict[str, str] = {}
        # no-more-int-3 A1: dict var -> WhyML value type ν, captured only for a
        # NON-int real value type (currently `string`) from a `Dict[K, V]`
        # annotation — `_get_type_name` discards V. Int-valued dicts get no entry
        # and keep the existing `map int (option int)` path (byte-identical).
        self.current_dict_value_types: Dict[str, str] = {}
        # no-more-int-3 A1 T1.2: dict var -> WhyML key type κ (string), from
        # `Dict[str, V]`. Int-keyed dicts get no entry (default int key).
        self.current_dict_key_types: Dict[str, str] = {}
        self.current_function_name: str = ""
        self._class_fields: Dict[str, str] = {}
        # Module-level concurrency state
        self._shared_vars: Dict[str, Optional[str]] = {}   # var_name → mutex (or None)
        self._mutex_invariants: Dict[str, CSLNode] = {}    # mutex_name → invariant expr
        self._lock_order: Optional[List[str]] = None       # ordered list of mutex names
        # Module-level integer constants (`K_IHDR = 0`) — single-assignment module
        # names bound to an int literal. Allowed in contracts (resolved to their
        # literal in Module 6), mirroring class-body constants.
        self._module_constants: Dict[str, int] = {}

    def _get_type_name(self, annotation: ast.expr) -> str:
        """Extracts the type hint as a string.

        Bare names: returned as-is (`int`, `bool`, `str`, ...).
        Subscript: head identifier lowercased (`List[int]` → `list`,
        `Set[Mutex]` → `set`, `Dict[str, Any]` → `dict`, `Tuple[int, int]`
        → `tuple`, `FrozenSet[T]` → `frozenset`). `Optional[T]` and
        `Union[T, None]` unwrap to the inner type. Anything else: `Any`."""
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
            return head.lower()
        return "Any"

    @staticmethod
    def _get_dict_value_type(annotation: ast.expr) -> Optional[str]:
        """For a `Dict[K, V]` annotation, return the WhyML value type ν of V when
        it is a NON-int real type worth threading (currently only `str` →
        `string`); else None. `_get_type_name` discards V, so this is the
        parallel capture feeding the parametric-map value type (no-more-int-3 A1).
        An int value (`Dict[_, int]`) returns None — int-valued dicts keep the
        default `map int (option int)` path. Key type κ is a separate sub-stage."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("Dict", "dict")
                and isinstance(annotation.slice, ast.Tuple)
                and len(annotation.slice.elts) == 2):
            v = annotation.slice.elts[1]
            if isinstance(v, ast.Name) and v.id == "str":
                return "string"
            # no-more-int A1-residual: a nested-dict value `Dict[Ki, Vi]` → the
            # pure Why3 map type `map κi (option νi)`. Why3's `map` is immutable,
            # so a map-valued map does NOT hit the mutable-aliasing wall an
            # `array int` value would. (κi/νi ∈ {int, string}; the `JObj`
            # enabler for json.)
            if (isinstance(v, ast.Subscript)
                    and isinstance(v.value, ast.Name)
                    and v.value.id in ("Dict", "dict")
                    and isinstance(v.slice, ast.Tuple)
                    and len(v.slice.elts) == 2):
                ki, vi = v.slice.elts
                kw = "string" if (isinstance(ki, ast.Name) and ki.id == "str") else "int"
                vw = "string" if (isinstance(vi, ast.Name) and vi.id == "str") else "int"
                return f"map {kw} (option {vw})"
            # no-more-int-7 §B′ (A1-residual): a `List[int]` value → an immutable
            # `seq int` SNAPSHOT (value-semantics boundary, ownership-discipline §3).
            # Why3's `seq` is pure, so — unlike a mutable `array int` — it can live
            # inside a `map`; the store site snapshots the array → seq.
            if (isinstance(v, ast.Subscript)
                    and isinstance(v.value, ast.Name)
                    and v.value.id in ("List", "list")
                    and isinstance(v.slice, ast.Name)
                    and v.slice.id == "int"):
                return "seq int"
        return None

    @staticmethod
    def _get_dict_key_type(annotation: ast.expr) -> Optional[str]:
        """For a `Dict[K, V]` annotation, return the WhyML key type κ of K when it
        is a non-int real type (currently only `str` → `string`), else None.
        Parallel to `_get_dict_value_type`; feeds the parametric-map key type
        (no-more-int-3 A1 T1.2). Why3 `string` has decidable equality, so
        `Map.get (m: map string ν) (k: string)` is well-formed."""
        if (isinstance(annotation, ast.Subscript)
                and isinstance(annotation.value, ast.Name)
                and annotation.value.id in ("Dict", "dict")
                and isinstance(annotation.slice, ast.Tuple)
                and len(annotation.slice.elts) == 2):
            k = annotation.slice.elts[0]
            if isinstance(k, ast.Name) and k.id == "str":
                return "string"
        return None

    def _validate_contract(self, contract: CSLNode, context_name: str, is_postcondition: bool = False) -> None:
        """Validates that a contract's variables exist and keywords are used correctly."""
        # 1. Check \result usage
        if contains_result(contract) and not is_postcondition:
            raise PyCSLSemanticError(
                f"Invalid use of '\\result' in {context_name}. It is only allowed in 'ensures'."
            )

        # 2. Check variable scope
        referenced_vars = extract_variables(contract)
        for var_name in referenced_vars:
            if (var_name not in self.current_scope
                    and var_name not in self._module_constants):
                raise PyCSLSemanticError(
                    f"Undefined variable '{var_name}' referenced in contract for {context_name}. "
                    f"Available variables in scope: {list(self.current_scope.keys())}"
                )

        # 2b/3. typed quantifier-binder resolution AND \valid/\separated/\length-on-dict
        #       base checks MIGRATED to the language-agnostic core
        #       (core_ir_semantic._check_contract_exprs) — they run on the IR via a
        #       surface-tracking walk that reconstructs the same context (refactor.md B4).

        # 4. Check \proj index is a literal. NOT migrated: this is a PRECONDITION GUARD
        #    Module 5 depends on (ProjExpr emission reads index.value), so it must run
        #    before Module 5 — it stays here (refactor.md: needs Module-5 hardening first).
        self._validate_proj_indices(contract, context_name)

    def _validate_proj_indices(self, node: CSLNode, context_name: str) -> None:
        """Recursively check that all \\proj index arguments are integer literals."""
        if isinstance(node, ProjExpr):
            if not isinstance(node.index, Number):
                raise PyCSLSemanticError(
                    f"\\proj index must be an integer literal in {context_name}. "
                    "Dynamic projection is not supported."
                )
        for child in _iter_csl_children(node):
            self._validate_proj_indices(child, context_name)

    # `_validate_predicate_bases` MIGRATED to the language-agnostic core
    # (`core_ir_semantic._check_predicate_bases`) — `\length`-on-dict/set and
    # `\valid`/`\separated` base typing now run on the IR via a surface-tracking
    # walk that reconstructs the function / while-loop / ghost context (refactor.md B4).

    # ── Concurrency helpers ────────────────────────────────────────────────

    def _extract_held_mutexes(self, stmts: list) -> Set[str]:
        """Return the set of mutexes acquired via #@ acquires or #@ critical in stmts."""
        held = set()
        for stmt in stmts:
            if isinstance(stmt, ast.With):
                m = getattr(stmt, 'csl_critical_mutex', None) or getattr(stmt, 'csl_acquires', None)
                if m:
                    held.add(m)
        return held

    def _check_protected_in_stmts(self, stmts: list, held: Set[str], func_name: str) -> None:
        """Walk stmts, tracking held mutexes, and raise if a shared var is accessed unprotected."""
        for stmt in stmts:
            self._check_protected_in_stmt(stmt, held, func_name)

    _PROTECTED_HANDLERS: Dict[type, str] = {
        ast.With:       "_protected_with",
        ast.If:         "_protected_if",
        ast.While:      "_protected_loop",
        ast.For:        "_protected_loop",
        ast.Assign:     "_protected_assign",
        ast.AugAssign:  "_protected_aug_assign",
        ast.Return:     "_protected_return",
        ast.Expr:       "_protected_expr",
    }

    def _check_protected_in_stmt(self, node: ast.AST, held: Set[str], func_name: str) -> None:
        handler_name = self._PROTECTED_HANDLERS.get(type(node))
        if handler_name:
            getattr(self, handler_name)(node, held, func_name)

    def _protected_with(self, node: ast.With, held: Set[str], func_name: str) -> None:
        mutex = getattr(node, 'csl_critical_mutex', None) or getattr(node, 'csl_acquires', None)
        inner_held = held | {mutex} if mutex else held
        if mutex and held and self._lock_order is None:
            raise PyCSLSemanticError(
                f"Function '{func_name}': nested mutex acquisition of '{mutex}' while holding "
                f"{sorted(held)} requires a module-level '#@ lock_order' declaration."
            )
        if mutex and held and self._lock_order is not None:
            order = self._lock_order
            for already_held in held:
                ah_idx = order.index(already_held) if already_held in order else -1
                new_idx = order.index(mutex) if mutex in order else -1
                if ah_idx >= 0 and new_idx >= 0 and new_idx <= ah_idx:
                    raise PyCSLSemanticError(
                        f"Function '{func_name}': lock_order violation — acquiring '{mutex}' "
                        f"while holding '{already_held}' violates declared order {order}."
                    )
        self._check_protected_in_stmts(node.body, inner_held, func_name)

    def _protected_if(self, node: ast.If, held: Set[str], func_name: str) -> None:
        self._check_protected_in_stmts(node.body, held, func_name)
        self._check_protected_in_stmts(node.orelse, held, func_name)

    def _protected_loop(self, node: ast.AST, held: Set[str], func_name: str) -> None:
        self._check_protected_in_stmts(node.body, held, func_name)

    def _protected_assign(self, node: ast.Assign, held: Set[str], func_name: str) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._check_shared_access(target.id, held, func_name, write=True)
        self._check_expr_for_shared(node.value, held, func_name)

    def _protected_aug_assign(self, node: ast.AugAssign, held: Set[str], func_name: str) -> None:
        if isinstance(node.target, ast.Name):
            self._check_shared_access(node.target.id, held, func_name, write=True)

    def _protected_return(self, node: ast.Return, held: Set[str], func_name: str) -> None:
        if node.value:
            self._check_expr_for_shared(node.value, held, func_name)

    def _protected_expr(self, node: ast.Expr, held: Set[str], func_name: str) -> None:
        self._check_expr_for_shared(node.value, held, func_name)

    def _check_shared_access(self, var_name: str, held: Set[str], func_name: str, write: bool = False) -> None:
        if var_name not in self._shared_vars:
            return
        req_mutex = self._shared_vars[var_name]
        if req_mutex is None:
            return  # unprotected shared — ConcurrencyChecker will warn; SemanticAnalyzer is lenient
        if req_mutex not in held:
            action = "write to" if write else "read of"
            raise PyCSLSemanticError(
                f"Function '{func_name}': unprotected {action} shared variable '{var_name}' "
                f"(protected_by '{req_mutex}', but held mutexes are {sorted(held) or 'none'})."
            )

    def _check_expr_for_shared(self, node: ast.AST, held: Set[str], func_name: str) -> None:
        if isinstance(node, ast.Name):
            self._check_shared_access(node.id, held, func_name, write=False)
        for child in ast.iter_child_nodes(node):
            self._check_expr_for_shared(child, held, func_name)

    def _validate_mutex_invariant_scope(self, mutex: str, invariant: CSLNode, func_name: str) -> None:
        """Check that the invariant for 'mutex' only references variables protected by that mutex."""
        protected = {v for v, m in self._shared_vars.items() if m == mutex or
                     (m is not None and m.split('[')[0] == mutex.split('[')[0])}
        referenced = extract_variables(invariant)
        # Allow quantifier-bound variables (Forall/Exists) and numeric variables — be lenient
        for var in referenced:
            if var in self.current_scope or var in protected:
                continue
            # Allow single-letter loop variables common in invariants
            if len(var) <= 2:
                continue
            raise PyCSLSemanticError(
                f"Mutex invariant for '{mutex}': variable '{var}' is not a shared variable "
                f"protected by '{mutex}'. Protected variables: {sorted(protected)}."
            )

    def visit_Module(self, node: ast.Module) -> Any:
        """Collect module-level concurrency declarations."""
        self._shared_vars = {}
        self._mutex_invariants = {}
        self._lock_order = None
        self._module_constants = collect_module_constants(node)

        # quantification.md: the set a typed quantifier binder may resolve to —
        # scalars + declared `#@ datatype` names + class names. An unresolved binder
        # type is a hard error (never a silent `int`); see `_validate_quant_binders`.
        self._known_binder_types = (
            {"int", "bool", "str", "float"}
            # 07-1311 Q4: collection-typed binders — `\forall a: list; …` (array int),
            # `\forall m: dict; …` (map int (option int)). Lowered by Module6's
            # `_quant_binder_whyml`; these are faithful WhyML sorts, not int.
            | {"list", "bytes", "bytearray", "dict"}
            | {d.name for d in getattr(node, 'csl_datatypes', [])}
            | {c.name for c in node.body if isinstance(c, ast.ClassDef)})
        # lemma.md §7.5: names of `#@ \trusted` functions, so `_validate_lemma` can
        # reject a plain lemma body that rests on an unverified (trusted) fact.
        self._trusted_funcs = {
            n.name for n in ast.walk(node)
            if isinstance(n, ast.FunctionDef) and getattr(n, 'csl_trusted', False)}

        for decl in getattr(node, 'csl_shared_decls', []):
            self._shared_vars[decl.variable] = decl.mutex

        for mutex, inv_expr in getattr(node, 'csl_mutex_invariants', {}).items():
            self._mutex_invariants[mutex] = inv_expr
            self._validate_mutex_invariant_scope(mutex, inv_expr, "<module>")

        lock_order_node = getattr(node, 'csl_lock_order', None)
        if lock_order_node is not None:
            self._lock_order = lock_order_node.order

        self._validate_happy(node)

        self.generic_visit(node)

    def _validate_happy(self, node: ast.Module) -> None:
        """Validate module-level HAPPY declarations (meta.md Stage B). Each exempt
        name must be a real method (a typo would silently widen coverage — a hard
        error); the target field should be written somewhere (else the HAPPY is inert
        — a warning)."""
        happy = getattr(node, 'csl_happy_properties', [])
        if not happy:
            return
        method_names: Set[str] = set()
        written_fields: Set[str] = set()
        exec_methods: Set[str] = set()   # 07-1839 P5/HAPPY taint
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                method_names.add(n.name)
                # A dynamic exec (constant execs are already spliced away by P5b before
                # Module4) can write ANYTHING, so a method containing one is a worst-case
                # mutator w.r.t. any HAPPY region.
                for sub in ast.walk(n):
                    if (isinstance(sub, ast.Call)
                            and isinstance(getattr(sub, "func", None), ast.Name)
                            and sub.func.id == "exec"):
                        exec_methods.add(n.name)
                        break
            tgts = []
            if isinstance(n, ast.Assign):
                tgts = n.targets
            elif isinstance(n, (ast.AnnAssign, ast.AugAssign)):
                tgts = [n.target]
            for t in tgts:
                if (isinstance(t, ast.Subscript)
                        and isinstance(t.value, ast.Attribute)
                        and isinstance(t.value.value, ast.Name)
                        and t.value.value.id == "self"):
                    written_fields.add(t.value.attr)
        for hp in happy:
            for name in hp.except_set:
                if name not in method_names:
                    raise PyCSLSemanticError(
                        f"`happy {hp.name}`: exempt function '{name}' is not a method "
                        f"in this module. Known methods: {sorted(method_names)}. "
                        f"A typo in the exempt set would silently widen the property's "
                        f"coverage, so this is rejected."
                    )
            # 07-1839 P5/HAPPY taint: a non-exempt method with a dynamic `exec(...)` may
            # write anything, so it cannot be confined by this property — same teeth as a
            # non-exempt `\trusted` mutator without `#@ \preserves` (test 0462). It must be
            # in the except set (or have its exec removed / made a constant the P5b splice
            # can bound).
            for m in sorted(exec_methods):
                if m not in hp.except_set:
                    raise PyCSLSemanticError(
                        f"`happy {hp.name}`: method '{m}' contains a dynamic `exec(...)`, "
                        f"which may write anything (not a compile-time-constant exec, so it "
                        f"cannot be spliced/bounded). A non-exempt dynamic-exec method cannot "
                        f"be confined by this property — add it to the except set or remove the "
                        f"exec. (07-1839 P5 — exec is a worst-case mutator under HAPPY.)"
                    )
            # 07-1143 R1/R2: the `protects` form has no single `self.<field>`; its
            # write-site coverage (dotted paths) is validated by Module3's meta-pass.
            # An empty protected write set is legitimately inert (e.g. a subsystem with
            # no non-exempt writers), so do not warn for the protects form.
            if hp.protects is not None:
                continue
            if hp.field not in written_fields:
                warnings.warn(
                    f"`happy {hp.name}`: no write to `self.{hp.field}[...]` found in "
                    f"this module — the property expands to zero obligations (inert). "
                    f"Check the field name.",
                    stacklevel=2,
                )

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Collect field types from __init__, validate class invariants, then validate methods."""
        self._class_fields = self._collect_class_field_types(node)

        for inv in getattr(node, 'csl_class_invariants', []):
            context = f"class invariant for '{node.name}'"
            referenced = extract_variables(inv.expr)
            for var_name in referenced:
                if var_name not in self._class_fields:
                    raise PyCSLSemanticError(
                        f"Undefined variable '{var_name}' in {context}. "
                        f"Class invariants should only reference self.field or constants. "
                        f"Available fields: {list(self._class_fields.keys())}"
                    )

        self.generic_visit(node)
        self._class_fields = {}

    def _collect_class_field_types(self, node: ast.ClassDef) -> Dict[str, str]:
        """Scan __init__ for self.x assignments and return {field_name: type_name}."""
        fields: Dict[str, str] = {}
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                for stmt in ast.walk(child):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (isinstance(target, ast.Attribute) and
                                    isinstance(target.value, ast.Name) and
                                    target.value.id == 'self'):
                                fields[target.attr] = 'Any'
                    elif isinstance(stmt, ast.AnnAssign):
                        if (isinstance(stmt.target, ast.Attribute) and
                                isinstance(stmt.target.value, ast.Name) and
                                stmt.target.value.id == 'self'):
                            fields[stmt.target.attr] = (
                                self._get_type_name(stmt.annotation)
                                if stmt.annotation else 'Any'
                            )
        return fields

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        saved_scope = self.current_scope
        saved_dict_value_types = self.current_dict_value_types
        saved_dict_key_types = self.current_dict_key_types
        saved_function_name = self.current_function_name
        self.current_function_name = f"function '{node.name}'"
        self.current_scope = {}
        self.current_dict_value_types = {}
        self.current_dict_key_types = {}

        self._build_function_scope(node)
        self._validate_no_mutable_defaults(node)
        self._validate_lemma(node)
        self._validate_function_contracts(node)
        # assigns-region base typing + subscript-assignment base typing migrated to
        # core_ir_semantic (refactor.md B3 / AST-only #3)

        node.csl_symbol_table = self.current_scope.copy()
        node.csl_dict_value_types = self.current_dict_value_types.copy()
        node.csl_dict_key_types = self.current_dict_key_types.copy()

        if self._shared_vars:
            self._check_protected_in_stmts(node.body, set(), node.name)

        self.generic_visit(node)

        self.current_scope = saved_scope
        self.current_dict_value_types = saved_dict_value_types
        self.current_dict_key_types = saved_dict_key_types
        self.current_function_name = saved_function_name

    def _validate_lemma(self, node: ast.FunctionDef) -> None:
        """lemma.md §3 — soundness/well-formedness checks for a `#@ lemma`. Enforced:

          • **`\\diverges` forbidden (§7.3).** A non-terminating lemma proves nothing.
          • **Shape (§7.1).** At least one `#@ ensures` (the conclusion).
          • **Ghost discipline (§7.4).** Return type `None` (a lemma computes nothing →
            WhyML `unit`), `assigns \\nothing`, and no `return <value>` in the body.
          • **No trust-leakage (§7.5).** A plain `#@ lemma` body may not call a
            `\\trusted` function — that would smuggle an *unverified* fact into a
            "proved" lemma (Why3 cannot catch this; the trusted `val`'s contract is
            axiomatic). [`#@ lemma \\trusted` shim — assumed+warned — is unimplemented.]

        NOT a soundness check (Why3 owns it; remains-2.md decision A): the
        variant-on-recursion requirement is intentionally NOT enforced — Why3 infers
        structural variants and rejects ill-founded recursion via its termination VC,
        so requiring `#@ \\variant` was redundant and over-restrictive.

        Deferred (Why3-enforced, like inductive positivity): the contract-call-position
        ban — using a lemma name as a term in a `#@ requires`/`#@ ensures` is rejected
        by Why3 (a `let lemma` is not a usable term)."""
        if not getattr(node, 'csl_lemma', False):
            return
        name = node.name
        if getattr(node, 'csl_diverges', False):
            raise PyCSLSemanticError(
                f"`#@ lemma` '{name}' is also `#@ \\diverges`: a non-terminating "
                f"lemma proves nothing and would be unsound as a fact. Remove one.")
        if not getattr(node, 'csl_ensures', []):
            raise PyCSLSemanticError(
                f"`#@ lemma` '{name}' has no `#@ ensures`: a lemma must state the "
                f"fact it proves (the conclusion). Add at least one `#@ ensures`.")
        # Ghost discipline: a lemma returns unit.
        ret = node.returns
        if not (ret is None or (isinstance(ret, ast.Constant) and ret.value is None)):
            raise PyCSLSemanticError(
                f"`#@ lemma` '{name}' must be annotated `-> None`: a lemma computes "
                f"nothing (its WhyML result is `unit`); the body is the proof.")
        for a in getattr(node, 'csl_assigns', []):
            for t in getattr(a, 'targets', []):
                if not isinstance(t, Nothing):
                    raise PyCSLSemanticError(
                        f"`#@ lemma` '{name}' must be `assigns \\nothing`: a lemma is "
                        f"erased at extraction and may not mutate non-ghost state.")
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and n.value is not None and not (
                    isinstance(n.value, ast.Constant) and n.value.value is None):
                raise PyCSLSemanticError(
                    f"`#@ lemma` '{name}' body must not `return` a value — it is a "
                    f"proof (returns unit). Use `pass` for an immediate arm.")
        # No trust-leakage: a plain lemma may not rest on a `\trusted` (unverified) fact.
        trusted = getattr(self, "_trusted_funcs", set())
        for n in ast.walk(node):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    and n.func.id in trusted):
                raise PyCSLSemanticError(
                    f"`#@ lemma` '{name}' calls `\\trusted` function '{n.func.id}': a "
                    f"checked lemma may not rest on an unverified (trusted) fact — that "
                    f"would smuggle an unchecked axiom into a 'proved' lemma.")

    def _validate_no_mutable_defaults(self, node: ast.FunctionDef) -> None:
        """Ownership R2 (crude enforcement, `docs/pycsl-ownership-discipline.md`
        §2/§5): a mutable default argument — `def f(x, acc=[])` (or `={}`/`=set()`
        /`=list(...)`/`=dict(...)`) — binds ONE mutable object shared across every
        call (the classic aliasing bug), outside the value-semantics boundary.
        Reject it at semantic analysis with a clear diagnostic rather than
        verifying it unsoundly or failing confusingly."""
        args = getattr(node, "args", None)
        if args is None:
            return
        defaults = list(getattr(args, "defaults", []) or [])
        defaults += [d for d in (getattr(args, "kw_defaults", []) or []) if d is not None]
        for d in defaults:
            mutable = isinstance(d, (ast.List, ast.Dict, ast.Set))
            if (isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
                    and d.func.id in ("list", "dict", "set")):
                mutable = True
            if mutable:
                raise PyCSLSemanticError(
                    f"Mutable default argument in {self.current_function_name}: a "
                    f"list/dict/set default is a single object shared across all "
                    f"calls (a shared-aliasing bug) and is outside PyCSL's "
                    f"value-semantics boundary (ownership discipline R2). Use a "
                    f"`None` sentinel and initialise the collection in the body.")

    def _build_function_scope(self, node: ast.FunctionDef) -> None:
        """Populate current_scope from function args, local assignments, and ghost variables."""
        # Function arguments (skip 'self' for methods)
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            arg_type = self._get_type_name(arg.annotation) if arg.annotation else "Any"
            self.current_scope[arg.arg] = arg_type
            if arg.annotation is not None:
                nu = self._get_dict_value_type(arg.annotation)
                if nu is not None:
                    self.current_dict_value_types[arg.arg] = nu
                kappa = self._get_dict_key_type(arg.annotation)
                if kappa is not None:
                    self.current_dict_key_types[arg.arg] = kappa

        # Local variables (skip shared module-level variables)
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and target.id not in self._shared_vars:
                        self.current_scope[target.id] = "Any"
            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name) and child.target.id not in self._shared_vars:
                    self.current_scope[child.target.id] = (
                        self._get_type_name(child.annotation)
                        if child.annotation else "Any"
                    )
                    if child.annotation is not None:
                        nu = self._get_dict_value_type(child.annotation)
                        if nu is not None:
                            self.current_dict_value_types[child.target.id] = nu
                        kappa = self._get_dict_key_type(child.annotation)
                        if kappa is not None:
                            self.current_dict_key_types[child.target.id] = kappa
            elif isinstance(child, ast.For):
                # For-loop iteration variables are in scope throughout the loop body
                if isinstance(child.target, ast.Name) and child.target.id not in self._shared_vars:
                    self.current_scope[child.target.id] = "Any"
                elif isinstance(child.target, ast.Tuple):
                    for elt in child.target.elts:
                        if isinstance(elt, ast.Name) and elt.id not in self._shared_vars:
                            self.current_scope[elt.id] = "Any"

        # Ghost variables — register all targets first, then validate values.
        # Only declarations (op == "=") carry a meaningful declared_type; augmented
        # assignments must not overwrite a type that was already registered.
        for child in ast.walk(node):
            for ga in getattr(child, 'csl_ghost_assigns', []):
                if isinstance(ga, GhostArraySetDecl):
                    continue  # element-set has no declared_type; array var already registered
                dtype = getattr(ga, 'declared_type', 'int')
                if ga.target not in self.current_scope or ga.op == "=":
                    self.current_scope[ga.target] = dtype
        for child in ast.walk(node):
            for ga in getattr(child, 'csl_ghost_assigns', []):
                if isinstance(ga, GhostArraySetDecl):
                    # Validate index and value expressions
                    ctx = f"{self.current_function_name} (ghost '{ga.target}[...]')"
                    self._validate_contract(ga.index, ctx, is_postcondition=False)
                    self._validate_contract(ga.value, ctx, is_postcondition=False)
                    continue
                # String ghosts do not support +=/-=/*= shorthands; use ^ operator.
                if ga.op != "=" and self.current_scope.get(ga.target) == "string":
                    raise PyCSLSemanticError(
                        f"Ghost string variable '{ga.target}' does not support '{ga.op}' "
                        f"in {self.current_function_name}. "
                        "Use the ^ operator for string concatenation: "
                        f"#@ ghost {ga.target} = {ga.target} ^ expr"
                    )
                if ga.value is not None:
                    self._validate_contract(
                        ga.value,
                        f"{self.current_function_name} (ghost '{ga.target}')",
                        is_postcondition=False,
                    )

    def _validate_function_contracts(self, node: ast.FunctionDef) -> None:
        """Validate requires, ensures, assigns, and function variant contracts."""
        for req in getattr(node, 'csl_requires', []):
            self._validate_contract(req, self.current_function_name, is_postcondition=False)

        for ens in getattr(node, 'csl_ensures', []):
            self._validate_contract(ens, self.current_function_name, is_postcondition=True)

        for ass in getattr(node, 'csl_assigns', []):
            self._validate_contract(ass, self.current_function_name, is_postcondition=False)

        for fv in getattr(node, 'csl_function_variants', []):
            self._validate_contract(fv, self.current_function_name, is_postcondition=False)

        # no_exception checks migrated to core_ir_semantic (refactor.md B2)
        self._validate_acts(node)
        # checkpoint \result-ban MIGRATED to core_ir_semantic._check_checkpoints — it
        # walks the IR body's ProofAssert nodes (already in the IR, no plumbing),
        # refactor.md AST-only #3.

    def _validate_acts(self, node: ast.FunctionDef) -> None:
        """Validate `act`/`complete`/`disjoint` (run on the pre-desugar nodes
        stashed by Module3 on `node.csl_acts`). The desugared requires/ensures are
        already validated by `_validate_function_contracts`; here we check the
        act-specific well-formedness."""
        acts = getattr(node, 'csl_acts', []) or []
        if not acts:
            return
        from Module2_Parser import Act, Given, Complete, Disjoint
        where = self.current_function_name
        defined: Dict[str, Any] = {}
        for a in acts:
            if not isinstance(a, Act):
                continue
            if a.name in defined:
                raise PyCSLSemanticError(f"duplicate act name '{a.name}' in {where}.")
            defined[a.name] = a
            for cl in a.clauses:
                if isinstance(cl, Given) and contains_result(cl.expr):
                    raise PyCSLSemanticError(
                        f"act '{a.name}' in {where}: '\\result' is not allowed in a "
                        f"'given' guard (guards are evaluated in the pre-state).")
        meta = [a for a in acts if isinstance(a, (Complete, Disjoint))]
        referenced: Set[str] = set()
        for m in meta:
            kind = "complete" if isinstance(m, Complete) else "disjoint"
            for nm in m.names:
                referenced.add(nm)
                if nm not in defined:
                    raise PyCSLSemanticError(
                        f"`{kind}` in {where} references undefined act '{nm}'.")
        # Mistyped-name / omission guard: if the author uses complete/disjoint at
        # all, an act left out of them is likely a typo — warn (not an error,
        # since declaring cases without claiming coverage is legitimate).
        if meta:
            for nm in defined:
                if nm not in referenced:
                    warnings.warn(
                        f"act '{nm}' in {where} is not referenced by any "
                        f"`complete`/`disjoint` — possible typo or omission.",
                        stacklevel=2)

    # `_validate_no_exception` MIGRATED to the language-agnostic core
    # (`core_ir_semantic.run_ir_semantic_checks` → `_check_no_exception`) — the
    # no_exception well-formedness checks now run on the IR, not the AST
    # (refactor.md Phase B, brick B2). The IR carries the contract data
    # (no_exception / no_exception_all / raises[].exc_type) and the §4.4 span, so
    # the identical errors are reported from the core.

    # `_validate_assigns_regions` MIGRATED to the language-agnostic core
    # (`core_ir_semantic._check_assigns_regions`) — assigns-region base typing now
    # runs on the IR (assigns targets + symbol_table), not the AST (refactor.md B3).

    # `_validate_subscript_assignments` MIGRATED to the language-agnostic core
    # (`core_ir_semantic._check_subscript_assignments`) — the `arr[i] = v` base-typing
    # check now walks the IR body's `ArraySet` nodes (no plumbing needed; the data was
    # already in the IR), gated to annotated functions (refactor.md B / AST-only #3).

    def visit_While(self, node: ast.While) -> Any:
        context_name = f"while loop at line {node.lineno} inside {self.current_function_name}"
        
        # Validate Loop Contracts against the current function scope
        for inv in getattr(node, 'csl_invariants', []):
            self._validate_contract(inv, context_name, is_postcondition=False)
            
        for var in getattr(node, 'csl_variants', []):
            self._validate_contract(var, context_name, is_postcondition=False)

        self.generic_visit(node)

    def process(self, tree: ast.AST) -> ast.AST:
        """Runs the semantic analysis on the unified AST."""
        self.visit(tree)
        return tree
