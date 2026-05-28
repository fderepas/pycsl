from __future__ import annotations

import ast
from typing import Callable, Dict, List, Optional, Set, Any
from Module2_Parser import (
    CSLNode, ContractWrapper, QuantifierNode, SingleExprNode,
    Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    Var, Result, Old, BinOp, UnaryOp, Nothing, Number, FieldAccess,
    ClassInvariant, Forall, Exists, ArrayLength, SubscriptAccess,
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
        self.current_function_name: str = ""
        self._class_fields: Dict[str, str] = {}
        # Module-level concurrency state
        self._shared_vars: Dict[str, Optional[str]] = {}   # var_name → mutex (or None)
        self._mutex_invariants: Dict[str, CSLNode] = {}    # mutex_name → invariant expr
        self._lock_order: Optional[List[str]] = None       # ordered list of mutex names

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
            if var_name not in self.current_scope:
                raise PyCSLSemanticError(
                    f"Undefined variable '{var_name}' referenced in contract for {context_name}. "
                    f"Available variables in scope: {list(self.current_scope.keys())}"
                )

        # 3. Check \valid and \separated base types
        self._validate_predicate_bases(contract, context_name)

        # 4. Check \proj index is always a literal
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

    def _validate_predicate_bases(self, node: CSLNode, context_name: str) -> None:
        """Recursively check that \\valid and \\separated reference list-typed parameters."""
        if isinstance(node, Valid):
            arr_type = self.current_scope.get(node.base)
            if arr_type not in ("list", "List", "Any", None):
                raise PyCSLSemanticError(
                    f"\\valid base '{node.base}' is not a list parameter "
                    f"in {context_name} (got type '{arr_type}')."
                )
        elif isinstance(node, Separated):
            for base in (node.base1, node.base2):
                arr_type = self.current_scope.get(base)
                if arr_type not in ("list", "List", "Any", None):
                    raise PyCSLSemanticError(
                        f"\\separated base '{base}' is not a list parameter "
                        f"in {context_name} (got type '{arr_type}')."
                    )
        for child in _iter_csl_children(node):
            self._validate_predicate_bases(child, context_name)

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

        for decl in getattr(node, 'csl_shared_decls', []):
            self._shared_vars[decl.variable] = decl.mutex

        for mutex, inv_expr in getattr(node, 'csl_mutex_invariants', {}).items():
            self._mutex_invariants[mutex] = inv_expr
            self._validate_mutex_invariant_scope(mutex, inv_expr, "<module>")

        lock_order_node = getattr(node, 'csl_lock_order', None)
        if lock_order_node is not None:
            self._lock_order = lock_order_node.order

        self.generic_visit(node)

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
        saved_function_name = self.current_function_name
        self.current_function_name = f"function '{node.name}'"
        self.current_scope = {}

        self._build_function_scope(node)
        self._validate_function_contracts(node)
        self._validate_assigns_regions(node)
        self._validate_subscript_assignments(node)

        node.csl_symbol_table = self.current_scope.copy()

        if self._shared_vars:
            self._check_protected_in_stmts(node.body, set(), node.name)

        self.generic_visit(node)

        self.current_scope = saved_scope
        self.current_function_name = saved_function_name

    def _build_function_scope(self, node: ast.FunctionDef) -> None:
        """Populate current_scope from function args, local assignments, and ghost variables."""
        # Function arguments (skip 'self' for methods)
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            arg_type = self._get_type_name(arg.annotation) if arg.annotation else "Any"
            self.current_scope[arg.arg] = arg_type

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

        self._validate_no_exception(node)

    def _validate_no_exception(self, node: ast.FunctionDef) -> None:
        """Validate `no_exception` directives:
        - each named exception must be in the Phase 1 known set
        - no_exception E and `raises { E -> _ }` for the same E is rejected
        - no_exception \\all and any raises clause is rejected
        """
        # Imported lazily so the module dependency surface stays small.
        from exception_model import KNOWN_EXCEPTIONS

        no_exc = list(getattr(node, 'csl_no_exception', []) or [])
        no_exc_all = bool(getattr(node, 'csl_no_exception_all', False))
        raises_list = list(getattr(node, 'csl_raises', []) or [])
        raised_names = {r.exc_type for r in raises_list}

        for name in no_exc:
            if name not in KNOWN_EXCEPTIONS:
                raise PyCSLSemanticError(
                    f"{self.current_function_name} (line {node.lineno}): "
                    f"no_exception names unknown exception '{name}'. "
                    f"Known: {sorted(KNOWN_EXCEPTIONS)}."
                )
            if name in raised_names:
                raise PyCSLSemanticError(
                    f"{self.current_function_name} (line {node.lineno}): "
                    f"contradictory annotations — no_exception {name} "
                    f"and raises {{ {name} -> ... }} cannot both apply."
                )
        if no_exc_all and raised_names:
            raise PyCSLSemanticError(
                f"{self.current_function_name} (line {node.lineno}): "
                f"no_exception \\all requires the raises set to be empty; "
                f"found raises {{ {', '.join(sorted(raised_names))} -> ... }}."
            )

    def _validate_assigns_regions(self, node: ast.FunctionDef) -> None:
        """Check that assigns region bases are list-typed parameters."""
        for ass in getattr(node, 'csl_assigns', []):
            for target in ass.targets:
                if isinstance(target, AssignsRegion):
                    arr_type = self.current_scope.get(target.base)
                    if arr_type is None:
                        raise PyCSLSemanticError(
                            f"Assigns region references undefined variable '{target.base}' "
                            f"in {self.current_function_name}."
                        )
                    if arr_type not in ("list", "List", "Any"):
                        raise PyCSLSemanticError(
                            f"Assigns region on non-list variable '{target.base}' "
                            f"(type '{arr_type}') in {self.current_function_name}."
                        )

    def _validate_subscript_assignments(self, node: ast.FunctionDef) -> None:
        """Check that arr[i] = v targets are list-typed variables (annotated functions only)."""
        has_annotations = (
            getattr(node, 'csl_requires', []) or
            getattr(node, 'csl_ensures', []) or
            getattr(node, 'csl_assigns', []) or
            getattr(node, 'csl_invariants', [])
        )
        if not has_annotations:
            return
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                        arr_name = target.value.id
                        arr_type = self.current_scope.get(arr_name)
                        if arr_type is None:
                            raise PyCSLSemanticError(
                                f"Subscript assignment to undefined variable '{arr_name}' "
                                f"in {self.current_function_name}."
                            )
                        if arr_type not in ("list", "List", "dict", "Dict",
                                             "Any"):
                            raise PyCSLSemanticError(
                                f"Subscript assignment to non-list/dict variable '{arr_name}' "
                                f"(type '{arr_type}') in {self.current_function_name}."
                            )

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
