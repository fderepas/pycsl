from dataclasses import dataclass
from typing import List, Union, Any, Optional
from lark import Lark, Transformer, v_args
from lark.exceptions import LarkError
from errors import PyCSLParseError

# ---------------------------------------------------------
# 1. Contract AST Nodes (The Internal Representation)
# ---------------------------------------------------------

@dataclass
class CSLNode:
    pass

class ContractWrapper(CSLNode): pass   # Requires, Ensures, LoopInvariant, LoopVariant
class QuantifierNode(CSLNode): pass    # Forall, Exists
class SingleExprNode(CSLNode): pass    # UnaryOp, Old

@dataclass
class Requires(ContractWrapper):
    expr: CSLNode

@dataclass
class Ensures(ContractWrapper):
    expr: CSLNode

@dataclass
class Assigns(CSLNode):
    targets: List[CSLNode]

@dataclass
class LoopInvariant(ContractWrapper):
    expr: CSLNode

@dataclass
class LoopVariant(ContractWrapper):
    expr: CSLNode

@dataclass
class BinOp(CSLNode):
    left: CSLNode
    op: str
    right: CSLNode

@dataclass
class UnaryOp(SingleExprNode):
    op: str
    expr: CSLNode

@dataclass
class Var(CSLNode):
    name: str

@dataclass
class Number(CSLNode):
    value: float

@dataclass
class StringLiteral(CSLNode):
    value: str

@dataclass
class Result(CSLNode):
    pass

@dataclass
class Old(SingleExprNode):
    expr: CSLNode

@dataclass
class Nothing(CSLNode):
    pass

@dataclass
class FieldAccess(CSLNode):
    object: str   # "self"
    field: str

@dataclass
class ClassInvariant(CSLNode):
    expr: CSLNode

@dataclass
class SubscriptAccess(CSLNode):
    array: str
    index: CSLNode

@dataclass
class Forall(QuantifierNode):
    var: str
    body: CSLNode

@dataclass
class Exists(QuantifierNode):
    var: str
    body: CSLNode

@dataclass
class ArrayLength(CSLNode):
    var: str

@dataclass
class AssignsRegion(CSLNode):
    """Represents `arr[lo..hi]` inside an assigns clause (frame condition region)."""
    base: str       # array parameter name
    low: CSLNode    # lower bound expression (inclusive)
    high: CSLNode   # upper bound expression (exclusive)

@dataclass
class Valid(CSLNode):
    """Represents `\\valid(arr, n)` — memory region [arr, arr+n) is allocated."""
    base: str
    length: CSLNode

@dataclass
class Separated(CSLNode):
    """Represents `\\separated(a, na, b, nb)` — regions [a,a+na) and [b,b+nb) don't overlap."""
    base1: str
    length1: CSLNode
    base2: str
    length2: CSLNode

@dataclass
class Label(CSLNode):
    """Represents a `#@ label L` program point annotation."""
    name: str

@dataclass
class At(CSLNode):
    """Represents `\\at(expr, L)` — value of expr at program point L."""
    expr: CSLNode
    label: str

@dataclass
class Length2D(CSLNode):
    """Represents `\\length2d(arr, m, n)` — arr has m rows each of length n."""
    base: str
    rows: CSLNode
    cols: CSLNode

@dataclass
class Valid2D(CSLNode):
    """Represents `\\valid2d(arr, i, j)` — (i,j) is a valid 2D index into arr."""
    base: str
    row: CSLNode
    col: CSLNode

@dataclass
class FunctionVariant(CSLNode):
    """Represents `#@ \\variant <expr>` or `#@ \\variant (<expr>, <ordering>)`."""
    expr: CSLNode
    ordering: Optional[str] = None   # None → integer, str → named well-founded relation

@dataclass
class Diverges(CSLNode):
    """Represents `#@ \\diverges` — function may not terminate."""
    pass

@dataclass
class Trusted(CSLNode):
    """Represents `#@ \\trusted` — function body is not verified."""
    pass

@dataclass
class CSLBool(CSLNode):
    """Represents True/False literals in contract expressions."""
    value: bool

@dataclass
class CSLNone(CSLNode):
    """Represents None literal in contract expressions."""
    pass

@dataclass
class CSLIn(CSLNode):
    """Represents `x in arr` membership test in contracts."""
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLNotIn(CSLNode):
    """Represents `x not in arr` negated membership test in contracts."""
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLSlice(CSLNode):
    """Represents `arr[lo:hi]` slice notation in contracts."""
    collection: str
    low: CSLNode
    high: CSLNode

@dataclass
class ChainedSubscript(CSLNode):
    """Represents `arr[i][j]` chained subscript access (2D array element)."""
    array: str
    index1: CSLNode
    index2: CSLNode

@dataclass
class CallExpr(CSLNode):
    """Represents a function call in a contract expression."""
    func: str
    args: List[CSLNode]

@dataclass
class IsSorted(CSLNode):
    """Represents `\\is_sorted(a, lo, hi)` — array is sorted in range."""
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class Sum(CSLNode):
    """Represents `\\sum(a, lo, hi)` — sum of array elements in range."""
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class GhostAssignDecl(CSLNode):
    """Represents `ghost var = expr` or `ghost var += expr` in contracts."""
    target: str
    value: CSLNode
    op: str  # "=" or "+=" or "-=" or "*="

@dataclass
class RaisesDecl(CSLNode):
    """Represents `raises ExcType when condition` in contracts."""
    exc_type: str
    condition: CSLNode

@dataclass
class BoundedIntDecl(CSLNode):
    """Represents `assumes bounded_int(N)` in contracts."""
    size: int

# --- Concurrency annotation nodes ---

@dataclass
class SharedDecl(CSLNode):
    """Represents `shared VAR protected_by MUTEX` or `shared VAR` (unprotected)."""
    variable: str
    mutex: Optional[str] = None

@dataclass
class ThreadEntry(CSLNode):
    """Represents `thread_entry` — marks a function as a concurrent thread entry point."""
    pass

@dataclass
class Acquires(CSLNode):
    """Represents `acquires MUTEX` — marks a mutex acquire point."""
    mutex: str

@dataclass
class Releases(CSLNode):
    """Represents `releases MUTEX` — marks a mutex release point."""
    mutex: str

@dataclass
class CriticalSection(CSLNode):
    """Represents `critical MUTEX` — marks a `with` block as a critical section."""
    mutex: str

@dataclass
class MutexInvariant(CSLNode):
    """Represents `mutex_invariant MUTEX: EXPR` — invariant held when mutex is unlocked."""
    mutex: str
    expr: CSLNode

@dataclass
class LockOrder(CSLNode):
    """Represents `lock_order M1, M2, ...` — total order on mutex acquisition to prevent deadlock."""
    order: List[str]

# ---------------------------------------------------------
# 2. The EBNF Grammar
# ---------------------------------------------------------

PYCSL_GRAMMAR = r"""
    ?start: contract

    ?contract: precondition
             | postcondition
             | assigns
             | loop_invariant
             | loop_variant
             | class_invariant
             | label_decl
             | function_variant
             | function_variant_structural
             | diverges_decl
             | trusted_decl
             | ghost_assign
             | ghost_aug_assign
             | raises_decl
             | bounded_int_decl
             | shared_decl
             | thread_entry_decl
             | acquires_decl
             | releases_decl
             | critical_decl
             | mutex_invariant_decl
             | lock_order_decl

    precondition: "requires" expr
    postcondition: "ensures" expr
    
    // Extracted alias from group to prevent Lark GrammarError
    assigns: "assigns" assigns_target
    ?assigns_target: assigns_region_list
                   | expr_list 
                   | "\\nothing" -> nothing

    assigns_region_list: assigns_region ("," assigns_region)*
    assigns_region: CNAME "[" expr RANGE_OP expr "]"

    loop_invariant: "loop" "invariant" expr
    loop_variant: "loop" "variant" expr
    class_invariant: "class" "invariant" expr
    label_decl: "label" CNAME
    function_variant: "\\variant" expr
    function_variant_structural: "\\variant" "(" expr "," CNAME ")"
    diverges_decl: "\\diverges"
    trusted_decl: "\\trusted"
    ghost_assign: "ghost" CNAME "=" expr
    ghost_aug_assign: "ghost" CNAME GHOST_AUG_OP expr
    raises_decl: "raises" CNAME "when" expr
    bounded_int_decl: "assumes" "bounded_int" "(" NUMBER ")"

    // Expression hierarchy (handles operator precedence and left-recursion)
    // Quantifiers can appear at top level or as the RHS of ==>, and, or.
    ?expr: implication
         | "\\forall" CNAME ";" expr -> forall_expr
         | "\\exists" CNAME ";" expr -> exists_expr
         | "\\exist"  CNAME ";" expr -> exists_expr

    ?implication: logical_or | implication IMPL_OP impl_rhs
    ?impl_rhs: logical_or
             | "\\forall" CNAME ";" expr -> forall_expr
             | "\\exists" CNAME ";" expr -> exists_expr
             | "\\exist"  CNAME ";" expr -> exists_expr

    ?logical_or: logical_and | logical_or OR_OP or_rhs
    ?or_rhs: logical_and
           | "\\forall" CNAME ";" expr -> forall_expr
           | "\\exists" CNAME ";" expr -> exists_expr
           | "\\exist"  CNAME ";" expr -> exists_expr

    ?logical_and: equality | logical_and AND_OP and_rhs
    ?and_rhs: equality
            | "\\forall" CNAME ";" expr -> forall_expr
            | "\\exists" CNAME ";" expr -> exists_expr
            | "\\exist"  CNAME ";" expr -> exists_expr
    ?equality: comparison | equality EQ_OP comparison
    ?comparison: membership | comparison COMP_OP membership
    ?membership: term
              | term "in" term -> in_expr
              | term "not" "in" term -> not_in_expr
    ?term: factor | term ADD_OP factor
    ?factor: unary | factor MUL_OP unary
    
    ?unary: UNARY_OP unary -> unary_op
          | atom

    ?atom: NUMBER -> number
         | ESCAPED_STRING -> string_literal
         | "True" -> true_lit
         | "False" -> false_lit
         | "None" -> none_lit
         | "self" "." CNAME -> field_access
         | "\\result" "[" expr "]" -> result_subscript
         | "\\is_sorted" "(" CNAME "," expr "," expr ")" -> is_sorted_expr
         | "\\sum" "(" CNAME "," expr "," expr ")" -> sum_expr
         | CNAME "(" expr_list ")" -> call_expr
         | CNAME "(" ")" -> call_expr_noargs
         | CNAME "[" expr ":" expr "]" -> slice_access
         | CNAME "[" expr "]" "[" expr "]" -> chained_subscript
         | CNAME "[" expr "]" -> subscript_access
         | CNAME -> var
         | "\\result" -> result
         | "\\old" "(" expr ")" -> old_var
         | "\\length" "(" CNAME ")" -> array_length
         | "\\valid" "(" CNAME "," expr ")" -> valid_pred
         | "\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred
         | "\\at" "(" expr "," CNAME ")" -> at_expr
         | "\\length2d" "(" CNAME "," expr "," expr ")" -> length2d_pred
         | "\\valid2d" "(" CNAME "," expr "," expr ")" -> valid2d_pred
         | "(" expr ")"

    expr_list: expr ("," expr)*

    // Concurrency annotations
    mutex_expr: CNAME "[" expr "]" -> mutex_subscript
              | CNAME -> mutex_name

    shared_decl: "shared" CNAME "protected_by" mutex_expr -> shared_protected
               | "shared" CNAME -> shared_unprotected
    thread_entry_decl: "thread_entry"
    acquires_decl: "acquires" mutex_expr
    releases_decl: "releases" mutex_expr
    critical_decl: "critical" mutex_expr
    mutex_invariant_decl: "mutex_invariant" mutex_expr ":" expr
    lock_order_decl: "lock_order" mutex_expr ("," mutex_expr)*

    // Explicit tokens so Lark doesn't drop the operators
    IMPL_OP: "==>" | "<==>"
    OR_OP: "or"
    AND_OP: "and"
    EQ_OP: "==" | "!="
    COMP_OP: ">" | "<" | ">=" | "<="
    ADD_OP: "+" | "-"
    MUL_OP: "*" | "//" | "/" | "%"
    UNARY_OP: "not" | "-" | "+"
    RANGE_OP: ".."
    GHOST_AUG_OP: "+=" | "-=" | "*="

    %import common.CNAME
    %import common.INT -> NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""

def _csl_to_str(node) -> str:
    """Convert a simple CSL node to string — used for mutex subscript indices."""
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Number):
        return str(int(node.value))
    if isinstance(node, BinOp):
        return f"{_csl_to_str(node.left)}{node.op}{_csl_to_str(node.right)}"
    return "?"


# ---------------------------------------------------------
# 3. The Tree Transformer
# ---------------------------------------------------------

@v_args(inline=True)
class PyCSLTransformer(Transformer):
    """Converts Lark's ParseTree into our Contract AST Nodes."""
    
    def precondition(self, expr) -> Requires: return Requires(expr)
    def postcondition(self, expr) -> Ensures: return Ensures(expr)

    def assigns(self, target) -> Assigns:
        if isinstance(target, Nothing):
            return Assigns([target])
        elif isinstance(target, list):
            return Assigns(target)
        else:
            return Assigns([target])

    def loop_invariant(self, expr) -> LoopInvariant: return LoopInvariant(expr)
    def loop_variant(self, expr) -> LoopVariant: return LoopVariant(expr)
    def class_invariant(self, expr) -> ClassInvariant: return ClassInvariant(expr)
    def function_variant(self, expr) -> FunctionVariant: return FunctionVariant(expr)
    def function_variant_structural(self, expr, ordering) -> FunctionVariant: return FunctionVariant(expr, str(ordering))
    def diverges_decl(self) -> Diverges: return Diverges()
    def trusted_decl(self) -> Trusted: return Trusted()
    def ghost_assign(self, name, expr) -> GhostAssignDecl: return GhostAssignDecl(str(name), expr, "=")
    def ghost_aug_assign(self, name, op, expr) -> GhostAssignDecl: return GhostAssignDecl(str(name), expr, str(op))
    def raises_decl(self, exc_type, condition) -> RaisesDecl: return RaisesDecl(str(exc_type), condition)
    def bounded_int_decl(self, size) -> BoundedIntDecl: return BoundedIntDecl(int(size))

    # Concurrency annotations
    def mutex_name(self, name) -> str: return str(name)
    def mutex_subscript(self, name, index) -> str:
        return f"{name}[{_csl_to_str(index)}]"
    def shared_protected(self, name, mutex) -> SharedDecl: return SharedDecl(str(name), str(mutex))
    def shared_unprotected(self, name) -> SharedDecl: return SharedDecl(str(name), None)
    def thread_entry_decl(self) -> ThreadEntry: return ThreadEntry()
    def acquires_decl(self, mutex) -> Acquires: return Acquires(str(mutex))
    def releases_decl(self, mutex) -> Releases: return Releases(str(mutex))
    def critical_decl(self, mutex) -> CriticalSection: return CriticalSection(str(mutex))
    def mutex_invariant_decl(self, mutex, expr) -> MutexInvariant: return MutexInvariant(str(mutex), expr)
    def lock_order_decl(self, *mutexes) -> LockOrder: return LockOrder([str(m) for m in mutexes])

    # Quantifiers
    def forall_expr(self, var, body) -> Forall: return Forall(str(var), body)
    def exists_expr(self, var, body) -> Exists: return Exists(str(var), body)
    def array_length(self, var) -> ArrayLength: return ArrayLength(str(var))
    def subscript_access(self, name, index) -> SubscriptAccess: return SubscriptAccess(str(name), index)
    def chained_subscript(self, name, index1, index2) -> ChainedSubscript: return ChainedSubscript(str(name), index1, index2)
    def slice_access(self, name, low, high) -> CSLSlice: return CSLSlice(str(name), low, high)
    def result_subscript(self, index) -> SubscriptAccess: return SubscriptAccess("\\result", index)
    def assigns_region(self, name, low, _op, high) -> AssignsRegion: return AssignsRegion(str(name), low, high)
    def assigns_region_list(self, *regions) -> List[AssignsRegion]: return list(regions)
    def valid_pred(self, name, length) -> Valid: return Valid(str(name), length)
    def separated_pred(self, name1, len1, name2, len2) -> Separated: return Separated(str(name1), len1, str(name2), len2)
    def label_decl(self, name) -> Label: return Label(str(name))
    def at_expr(self, expr, label) -> At: return At(expr, str(label))
    def length2d_pred(self, name, rows, cols) -> Length2D: return Length2D(str(name), rows, cols)
    def valid2d_pred(self, name, row, col) -> Valid2D: return Valid2D(str(name), row, col)

    # Operations
    def implication(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def logical_or(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def logical_and(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def equality(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def comparison(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def term(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    def factor(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    def unary_op(self, op, expr) -> UnaryOp: return UnaryOp(str(op), expr)

    # Atoms
    def number(self, n) -> Number: return Number(float(n))
    def string_literal(self, s) -> StringLiteral: return StringLiteral(str(s)[1:-1])  # strip quotes
    def true_lit(self) -> CSLBool: return CSLBool(True)
    def false_lit(self) -> CSLBool: return CSLBool(False)
    def none_lit(self) -> CSLNone: return CSLNone()
    def var(self, name) -> Var: return Var(str(name))
    def field_access(self, field_name) -> FieldAccess: return FieldAccess("self", str(field_name))
    def result(self) -> Result: return Result()
    def old_var(self, expr) -> Old: return Old(expr)
    def nothing(self) -> Nothing: return Nothing()

    # Membership
    def in_expr(self, element, collection) -> CSLIn: return CSLIn(element, collection)
    def not_in_expr(self, element, collection) -> CSLNotIn: return CSLNotIn(element, collection)

    # Function calls and built-in predicates
    def call_expr(self, name, args) -> CallExpr: return CallExpr(str(name), args if isinstance(args, list) else [args])
    def call_expr_noargs(self, name) -> CallExpr: return CallExpr(str(name), [])
    def is_sorted_expr(self, base, lo, hi) -> IsSorted: return IsSorted(str(base), lo, hi)
    def sum_expr(self, base, lo, hi) -> Sum: return Sum(str(base), lo, hi)

    def expr_list(self, *exprs) -> List[CSLNode]: return list(exprs)

# ---------------------------------------------------------
# 4. The Parser Interface
# ---------------------------------------------------------

class Module2_Parser:
    """Parses raw PyCSL string contracts into Contract AST objects."""
    def __init__(self) -> None:
        self.parser = Lark(PYCSL_GRAMMAR, parser='lalr', transformer=PyCSLTransformer())

    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return self.parser.parse(contract_str)
        except LarkError as e:
            raise PyCSLParseError(
                f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{str(e)}",
                line=line_number, stage="parse"
            ) from e

    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes
