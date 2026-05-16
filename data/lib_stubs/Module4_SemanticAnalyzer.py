"""PyCSL mock for Module4_SemanticAnalyzer."""
_ = 0  # anchor

# ── PyCSLSemanticError exception ────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PyCSLSemanticError(message: int) -> int:
    """Mock: create a PyCSLSemanticError."""
    return 0

# ── Utility functions ───────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def extract_variables(node: int) -> int:
    """Mock: extract variable names from a contract AST node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def contains_result(node: int) -> int:
    """Mock: check if result is used in an expression."""
    return 0

# ── Module4_SemanticAnalyzer class ──────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Module4_SemanticAnalyzer() -> int:
    """Mock: create a Module4_SemanticAnalyzer."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module4_SemanticAnalyzer_visit_ClassDef(self: int, node: int) -> int:
    """Mock: collect fields and validate class invariants."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module4_SemanticAnalyzer_visit_FunctionDef(self: int, node: int) -> int:
    """Mock: resolve scopes and validate function contracts."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module4_SemanticAnalyzer_visit_While(self: int, node: int) -> int:
    """Mock: validate loop contracts against current scope."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module4_SemanticAnalyzer_process(self: int, tree: int) -> int:
    """Mock: run semantic analysis on the unified AST."""
    return 0
