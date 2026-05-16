"""PyCSL mock for Module2_Parser."""
_ = 0  # anchor

# ── CSLNode dataclass hierarchy ─────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def CSLNode() -> int:
    """Mock: create a CSLNode base."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Requires(expr: int) -> int:
    """Mock: create a Requires node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Ensures(expr: int) -> int:
    """Mock: create an Ensures node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Assigns(targets: int) -> int:
    """Mock: create an Assigns node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def LoopInvariant(expr: int) -> int:
    """Mock: create a LoopInvariant node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def LoopVariant(expr: int) -> int:
    """Mock: create a LoopVariant node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def BinOp(left: int, op: int, right: int) -> int:
    """Mock: create a BinOp node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def UnaryOp(op: int, expr: int) -> int:
    """Mock: create a UnaryOp node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Var(name: int) -> int:
    """Mock: create a Var node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Number(value: int) -> int:
    """Mock: create a Number node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def StringLiteral(value: int) -> int:
    """Mock: create a StringLiteral node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Result() -> int:
    """Mock: create a Result node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Old(expr: int) -> int:
    """Mock: create an Old node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Nothing() -> int:
    """Mock: create a Nothing node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FieldAccess(object: int, field: int) -> int:
    """Mock: create a FieldAccess node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ClassInvariant(expr: int) -> int:
    """Mock: create a ClassInvariant node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def SubscriptAccess(array: int, index: int) -> int:
    """Mock: create a SubscriptAccess node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Forall(var: int, body: int) -> int:
    """Mock: create a Forall node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Exists(var: int, body: int) -> int:
    """Mock: create an Exists node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ArrayLength(var: int) -> int:
    """Mock: create an ArrayLength node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def AssignsRegion(base: int, low: int, high: int) -> int:
    """Mock: create an AssignsRegion node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Valid(base: int, length: int) -> int:
    """Mock: create a Valid node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Separated(base1: int, length1: int, base2: int, length2: int) -> int:
    """Mock: create a Separated node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Label(name: int) -> int:
    """Mock: create a Label node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def At(expr: int, label: int) -> int:
    """Mock: create an At node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Length2D(base: int, rows: int, cols: int) -> int:
    """Mock: create a Length2D node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Valid2D(base: int, row: int, col: int) -> int:
    """Mock: create a Valid2D node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def FunctionVariant(expr: int, ordering: int) -> int:
    """Mock: create a FunctionVariant node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Diverges() -> int:
    """Mock: create a Diverges node."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Trusted() -> int:
    """Mock: create a Trusted node."""
    return 0

# ── PyCSLTransformer class ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer() -> int:
    """Mock: create a PyCSLTransformer."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_precondition(self: int, expr: int) -> int:
    """Mock: transform precondition."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_postcondition(self: int, expr: int) -> int:
    """Mock: transform postcondition."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_assigns(self: int, target: int) -> int:
    """Mock: transform assigns clause."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_loop_invariant(self: int, expr: int) -> int:
    """Mock: transform loop invariant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_loop_variant(self: int, expr: int) -> int:
    """Mock: transform loop variant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_class_invariant(self: int, expr: int) -> int:
    """Mock: transform class invariant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_function_variant(self: int, expr: int) -> int:
    """Mock: transform function variant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_function_variant_structural(self: int, expr: int, ordering: int) -> int:
    """Mock: transform structural function variant."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_diverges_decl(self: int) -> int:
    """Mock: transform diverges declaration."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_trusted_decl(self: int) -> int:
    """Mock: transform trusted declaration."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_forall_expr(self: int, var: int, body: int) -> int:
    """Mock: transform forall expression."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_exists_expr(self: int, var: int, body: int) -> int:
    """Mock: transform exists expression."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_array_length(self: int, var: int) -> int:
    """Mock: transform array length."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_subscript_access(self: int, name: int, index: int) -> int:
    """Mock: transform subscript access."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_result_subscript(self: int, index: int) -> int:
    """Mock: transform result subscript."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_assigns_region(self: int, name: int, low: int, op: int, high: int) -> int:
    """Mock: transform assigns region."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_assigns_region_list(self: int) -> int:
    """Mock: transform assigns region list."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_valid_pred(self: int, name: int, length: int) -> int:
    """Mock: transform valid predicate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_separated_pred(self: int, name1: int, len1: int, name2: int, len2: int) -> int:
    """Mock: transform separated predicate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_label_decl(self: int, name: int) -> int:
    """Mock: transform label declaration."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_at_expr(self: int, expr: int, label: int) -> int:
    """Mock: transform at expression."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_length2d_pred(self: int, name: int, rows: int, cols: int) -> int:
    """Mock: transform length2d predicate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_valid2d_pred(self: int, name: int, row: int, col: int) -> int:
    """Mock: transform valid2d predicate."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_implication(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform implication."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_logical_or(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform logical or."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_logical_and(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform logical and."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_equality(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform equality."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_comparison(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform comparison."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_term(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform term."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_factor(self: int, left: int, op: int, right: int) -> int:
    """Mock: transform factor."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_unary_op(self: int, op: int, expr: int) -> int:
    """Mock: transform unary operation."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_number(self: int, n: int) -> int:
    """Mock: transform number."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_string_literal(self: int, s: int) -> int:
    """Mock: transform string literal."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_var(self: int, name: int) -> int:
    """Mock: transform variable."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_field_access(self: int, field_name: int) -> int:
    """Mock: transform field access."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_result(self: int) -> int:
    """Mock: transform result."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_old_var(self: int, expr: int) -> int:
    """Mock: transform old variable."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_nothing(self: int) -> int:
    """Mock: transform nothing."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PyCSLTransformer_expr_list(self: int) -> int:
    """Mock: transform expression list."""
    return 0

# ── Module2_Parser class ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def Module2_Parser() -> int:
    """Mock: create a Module2_Parser."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module2_Parser_parse_contract(self: int, contract_str: int, line_number: int) -> int:
    """Mock: parse a single contract string into a CSLNode."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def Module2_Parser_parse_node_contracts(self: int, raw_contracts: int, line_number: int) -> int:
    """Mock: parse a list of contract strings into CSLNode list."""
    return 0
