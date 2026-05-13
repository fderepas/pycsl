import ast
from typing import Dict, Set, Any
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    Var, Result, Old, BinOp, UnaryOp, Nothing, Number
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
    """
    if isinstance(node, Var):
        return {node.name}
    elif isinstance(node, BinOp):
        return extract_variables(node.left) | extract_variables(node.right)
    elif isinstance(node, UnaryOp) or isinstance(node, Old):
        return extract_variables(node.expr)
    elif isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)):
        return extract_variables(node.expr)
    elif isinstance(node, Assigns):
        vars_set = set()
        for target in node.targets:
            vars_set |= extract_variables(target)
        return vars_set
    return set()

def contains_result(node: CSLNode) -> bool:
    """Checks if \result is used anywhere in the expression."""
    if isinstance(node, Result): return True
    if isinstance(node, BinOp): return contains_result(node.left) or contains_result(node.right)
    if isinstance(node, UnaryOp) or isinstance(node, Old): return contains_result(node.expr)
    if isinstance(node, (Requires, Ensures, LoopInvariant, LoopVariant)): return contains_result(node.expr)
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.current_function_name = f"function '{node.name}'"
        self.current_scope = {}

        # 1. Populate scope with function arguments and their types
        for arg in node.args.args:
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
                    self.current_scope[child.target.id] = self._get_type_name(child.annotation) if child.annotation else "Any"

        # 3. Validate Function Contracts
        for req in getattr(node, 'csl_requires', []):
            self._validate_contract(req, self.current_function_name, is_postcondition=False)
            
        for ens in getattr(node, 'csl_ensures', []):
            self._validate_contract(ens, self.current_function_name, is_postcondition=True)
            
        for ass in getattr(node, 'csl_assigns', []):
            self._validate_contract(ass, self.current_function_name, is_postcondition=False)

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
