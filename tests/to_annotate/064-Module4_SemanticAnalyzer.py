import ast
from typing import Dict, Set, Any
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    Var, Result, Old, BinOp, UnaryOp, Nothing, Number, FieldAccess,
    ClassInvariant, Forall, Exists, ArrayLength, SubscriptAccess,
    AssignsRegion, Valid, Separated, FunctionVariant
)

# ---------------------------------------------------------
# 1. Custom Exceptions
# ---------------------------------------------------------

class PyCSLSemanticError(Exception):
    """Raised when a contract is semantically invalid (e.g., undefined variable)."""
    pass

# ---------------------------------------------------------
# 2. Contract Variable Extractor
# ---------------------------------------------------------

def extract_variables(node: CSLNode) -> Set[str]:
    """
    Recursively walks a Contract AST node and returns a set of all 
    variable names referenced within it.
    FieldAccess nodes (self.field) are excluded — validated separately.
    """
    if isinstance(node, Var):
        return {node.name}
    elif isinstance(node, FieldAccess):
        return set()
    elif isinstance(node, BinOp):
        return extract_variables(node.left) | extract_variables(node.right)
    elif isinstance(node, UnaryOp) or isinstance(node, Old):
        return extract_variables(node.expr)
    elif isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)):
        return extract_variables(node.expr)
    elif isinstance(node, FunctionVariant):
        return extract_variables(node.expr)
    elif isinstance(node, Assigns):
        vars_set = set()
        for target in node.targets:
            vars_set |= extract_variables(target)
        return vars_set
    elif isinstance(node, (Forall, Exists)):
        # Bound variable is not free — exclude it from the returned set
        return extract_variables(node.body) - {node.var}
    elif isinstance(node, ArrayLength):
        return {node.var}
    elif isinstance(node, SubscriptAccess):
        base = set() if node.array == "\\result" else {node.array}
        return base | extract_variables(node.index)
    elif isinstance(node, AssignsRegion):
        return {node.base} | extract_variables(node.low) | extract_variables(node.high)
    elif isinstance(node, Valid):
        return {node.base} | extract_variables(node.length)
    elif isinstance(node, Separated):
        return ({node.base1} | extract_variables(node.length1) |
                {node.base2} | extract_variables(node.length2))
    return set()

def contains_result(node: CSLNode) -> bool:
    """Checks if \\result is used anywhere in the expression."""
    if isinstance(node, Result): return True
    if isinstance(node, SubscriptAccess) and node.array == "\\result": return True
    if isinstance(node, BinOp): return contains_result(node.left) or contains_result(node.right)
    if isinstance(node, UnaryOp) or isinstance(node, Old): return contains_result(node.expr)
    if isinstance(node, SubscriptAccess): return contains_result(node.index)
    if isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)): return contains_result(node.expr)
    if isinstance(node, FunctionVariant): return contains_result(node.expr)
    return False

# ---------------------------------------------------------
# 3. The Semantic Analyzer (AST Pass)
# ---------------------------------------------------------

class Module4_SemanticAnalyzer(ast.NodeVisitor):
    """
    Walks the Annotated AST (AAST), resolves variable scopes, 
    extracts type hints, and validates contracts against them.
    """
    def __init__(self):
        # Keeps track of variables and their type hints in the current function
        self.current_scope: Dict[str, str] = {}
        self.current_function_name: str = ""
        # Fields collected from the current class's __init__ (name → type)
        self._class_fields: Dict[str, str] = {}

    def _get_type_name(self, annotation: ast.expr) -> str:
        """Extracts the type hint as a string (e.g., 'int', 'bool')."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        return "Any"

    def _validate_contract(self, contract: CSLNode, context_name: str, is_postcondition: bool = False):
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

    def _validate_predicate_bases(self, node: CSLNode, context_name: str):
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
        elif isinstance(node, BinOp):
            self._validate_predicate_bases(node.left, context_name)
            self._validate_predicate_bases(node.right, context_name)
        elif isinstance(node, (UnaryOp, Old)):
            self._validate_predicate_bases(node.expr, context_name)
        elif isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)):
            self._validate_predicate_bases(node.expr, context_name)
        elif isinstance(node, FunctionVariant):
            self._validate_predicate_bases(node.expr, context_name)
        elif isinstance(node, (Forall, Exists)):
            self._validate_predicate_bases(node.body, context_name)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Collect field types from __init__, validate class invariants, then validate methods."""
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
        self._class_fields = fields

        # Validate class invariants — only FieldAccess (self.field) and constants allowed
        for inv in getattr(node, 'csl_class_invariants', []):
            context = f"class invariant for '{node.name}'"
            referenced = extract_variables(inv.expr)
            for var_name in referenced:
                if var_name not in fields:
                    raise PyCSLSemanticError(
                        f"Undefined variable '{var_name}' in {context}. "
                        f"Class invariants should only reference self.field or constants. "
                        f"Available fields: {list(fields.keys())}"
                    )

        self.generic_visit(node)
        self._class_fields = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.current_function_name = f"function '{node.name}'"
        self.current_scope = {}

        # 1. Populate scope with function arguments (skip 'self' for methods)
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            arg_type = self._get_type_name(arg.annotation) if arg.annotation else "Any"
            self.current_scope[arg.arg] = arg_type

        # 2. Populate scope with local variables assigned in the function body
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        self.current_scope[target.id] = "Any"
            elif isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    self.current_scope[child.target.id] = (
                        self._get_type_name(child.annotation)
                        if child.annotation else "Any"
                    )

        # 4. Validate Function Contracts
        for req in getattr(node, 'csl_requires', []):
            self._validate_contract(req, self.current_function_name, is_postcondition=False)
            
        for ens in getattr(node, 'csl_ensures', []):
            self._validate_contract(ens, self.current_function_name, is_postcondition=True)
            
        for ass in getattr(node, 'csl_assigns', []):
            self._validate_contract(ass, self.current_function_name, is_postcondition=False)

        for fv in getattr(node, 'csl_function_variants', []):
            self._validate_contract(fv, self.current_function_name, is_postcondition=False)

        # Validate assigns regions: base must be a list-typed parameter
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

        # 5. Validate subscript assignments: arr[i] = v requires arr to be list-typed
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
                        if arr_type not in ("list", "List", "Any"):
                            raise PyCSLSemanticError(
                                f"Subscript assignment to non-list variable '{arr_name}' "
                                f"(type '{arr_type}') in {self.current_function_name}."
                            )

        # Attach the resolved symbol table to the node so the Backend can use it for SMT sorts!
        node.csl_symbol_table = self.current_scope.copy()

        self.generic_visit(node)

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
