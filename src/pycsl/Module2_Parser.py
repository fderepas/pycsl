from dataclasses import dataclass
from typing import List, Union, Any
from lark import Lark, Transformer, v_args
from lark.exceptions import LarkError

# ---------------------------------------------------------
# 1. Contract AST Nodes (The Internal Representation)
# ---------------------------------------------------------

@dataclass
class CSLNode:
    pass

@dataclass
class Requires(CSLNode):
    expr: CSLNode

@dataclass
class Ensures(CSLNode):
    expr: CSLNode

@dataclass
class Assigns(CSLNode):
    targets: List[CSLNode]

@dataclass
class LoopInvariant(CSLNode):
    expr: CSLNode

@dataclass
class LoopVariant(CSLNode):
    expr: CSLNode

@dataclass
class BinOp(CSLNode):
    left: CSLNode
    op: str
    right: CSLNode

@dataclass
class UnaryOp(CSLNode):
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
class Old(CSLNode):
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
class Forall(CSLNode):
    var: str
    body: CSLNode

@dataclass
class Exists(CSLNode):
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
    ordering: str = None   # None → integer, str → named well-founded relation

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
class CallExpr(CSLNode):
    """Represents a function call in a contract expression."""
    func: str
    args: list

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
         | CNAME "[" expr ":" expr "]" -> slice_access
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

    %import common.CNAME
    %import common.INT -> NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""

# ---------------------------------------------------------
# 3. The Tree Transformer
# ---------------------------------------------------------

@v_args(inline=True)
class PyCSLTransformer(Transformer):
    """Converts Lark's ParseTree into our Contract AST Nodes."""
    
    def precondition(self, expr): return Requires(expr)
    def postcondition(self, expr): return Ensures(expr)
    
    def assigns(self, target): 
        if isinstance(target, Nothing):
            return Assigns([target])
        elif isinstance(target, list):
            return Assigns(target)
        else:
            return Assigns([target])
            
    def loop_invariant(self, expr): return LoopInvariant(expr)
    def loop_variant(self, expr): return LoopVariant(expr)
    def class_invariant(self, expr): return ClassInvariant(expr)
    def function_variant(self, expr): return FunctionVariant(expr)
    def function_variant_structural(self, expr, ordering): return FunctionVariant(expr, str(ordering))
    def diverges_decl(self): return Diverges()
    def trusted_decl(self): return Trusted()

    # Quantifiers
    def forall_expr(self, var, body): return Forall(str(var), body)
    def exists_expr(self, var, body): return Exists(str(var), body)
    def array_length(self, var): return ArrayLength(str(var))
    def subscript_access(self, name, index): return SubscriptAccess(str(name), index)
    def slice_access(self, name, low, high): return CSLSlice(str(name), low, high)
    def result_subscript(self, index): return SubscriptAccess("\\result", index)
    def assigns_region(self, name, low, _op, high): return AssignsRegion(str(name), low, high)
    def assigns_region_list(self, *regions): return list(regions)
    def valid_pred(self, name, length): return Valid(str(name), length)
    def separated_pred(self, name1, len1, name2, len2): return Separated(str(name1), len1, str(name2), len2)
    def label_decl(self, name): return Label(str(name))
    def at_expr(self, expr, label): return At(expr, str(label))
    def length2d_pred(self, name, rows, cols): return Length2D(str(name), rows, cols)
    def valid2d_pred(self, name, row, col): return Valid2D(str(name), row, col)

    # Operations
    def implication(self, left, op, right): return BinOp(left, str(op), right)
    def logical_or(self, left, op, right): return BinOp(left, str(op), right)
    def logical_and(self, left, op, right): return BinOp(left, str(op), right)
    def equality(self, left, op, right): return BinOp(left, str(op), right)
    def comparison(self, left, op, right): return BinOp(left, str(op), right)
    def term(self, left, op, right): return BinOp(left, str(op), right)
    def factor(self, left, op, right): return BinOp(left, str(op), right)
    
    def unary_op(self, op, expr): return UnaryOp(str(op), expr)

    # Atoms
    def number(self, n): return Number(float(n))
    def string_literal(self, s): return StringLiteral(str(s)[1:-1])  # strip quotes
    def true_lit(self): return CSLBool(True)
    def false_lit(self): return CSLBool(False)
    def none_lit(self): return CSLNone()
    def var(self, name): return Var(str(name))
    def field_access(self, field_name): return FieldAccess("self", str(field_name))
    def result(self): return Result()
    def old_var(self, expr): return Old(expr)
    def nothing(self): return Nothing()
    
    # Membership
    def in_expr(self, element, collection): return CSLIn(element, collection)
    def not_in_expr(self, element, collection): return CSLNotIn(element, collection)
    
    def expr_list(self, *exprs): return list(exprs)

# ---------------------------------------------------------
# 4. The Parser Interface
# ---------------------------------------------------------

class Module2_Parser:
    """Parses raw PyCSL string contracts into Contract AST objects."""
    def __init__(self):
        self.parser = Lark(PYCSL_GRAMMAR, parser='lalr', transformer=PyCSLTransformer())

    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return self.parser.parse(contract_str)
        except LarkError as e:
            raise SyntaxError(f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{str(e)}")

    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes
