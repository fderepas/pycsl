"""PyCSL mock for Module5_IREmitter."""
_ = 0  # anchor

# ── PyCSLToJSONEmitter class ────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter() -> int:
    """Mock: create a PyCSLToJSONEmitter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter_visit_ClassDef(self: int, node: int) -> int:
    """Mock: emit IR for class definitions."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter_visit_FunctionDef(self: int, node: int) -> int:
    """Mock: emit IR for function definitions."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__csl_to_ir(self: int, node: int) -> int:
    """Mock: translate PyCSL nodes into IR dictionaries."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__csl_list_to_ir(self: int, csl_list: int) -> int:
    """Mock: translate a list of PyCSL nodes to IR."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__py_op_to_str(self: int, op: int) -> int:
    """Mock: convert Python AST operator to string."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__py_expr_to_ir(self: int, expr: int) -> int:
    """Mock: convert Python expression to IR dictionary."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__py_stmts_to_ir(self: int, stmts: int) -> int:
    """Mock: convert Python statements to IR list."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__process_while(self: int, node: int) -> int:
    """Mock: process while loop into IR."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__process_for(self: int, node: int) -> int:
    """Mock: process for loop into IR."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__process_if(self: int, node: int) -> int:
    """Mock: process if statement into IR."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__scan_2d_in_expr(self: int, expr: int, param_names: int, result: int) -> int:
    """Mock: scan expression for 2D array usage."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__scan_2d_in_stmt(self: int, stmt: int, param_names: int, result: int) -> int:
    """Mock: scan statement for 2D array usage."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLToJSONEmitter__collect_2d_params(self: int, body_ir: int, symbol_table: int) -> int:
    """Mock: collect 2D array parameters."""
    return 0

# ── Module5_IREmitter class ─────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Module5_IREmitter(tree: int) -> int:
    """Mock: create a Module5_IREmitter."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module5_IREmitter_generate_json(self: int, indent: int) -> int:
    """Mock: generate JSON IR from the annotated AST."""
    return 0
