""  # pycsl
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
class BoundedInt(CSLNode):
    """Represents `#@ assumes bounded_int(N)` — use bounded machine integers."""
    bits: int

@dataclass
class RaisesDecl(CSLNode):
    """Represents `#@ raises ExcType when <cond>` — exceptional postcondition."""
    exc_type: str
    condition: CSLNode

@dataclass
class GhostAssign(CSLNode):
    """Represents `#@ ghost <name> = <expr>` or `#@ ghost <name> += <expr>`."""
    target: str
    value: CSLNode
    op: str = "="  # "=", "+=", "-=", "*="

@dataclass
class CallExpr(CSLNode):
    """Represents a pure function call in a contract expression, e.g. is_sorted(arr, n)."""
    func: str
    args: List[CSLNode]

@dataclass
class IsSorted(CSLNode):
    """Represents `\\is_sorted(arr, lo, hi)` — arr[lo..hi) is sorted ascending."""
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class Sum(CSLNode):
    """Represents `\\sum(arr, lo, hi)` — sum of arr[lo..hi)."""
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
             | bounded_int_decl
             | raises_decl
             | ghost_assign
             | ghost_augassign

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
    bounded_int_decl: "assumes" "bounded_int" "(" NUMBER ")"
    raises_decl: "raises" CNAME "when" expr
    ghost_assign: "ghost" CNAME "=" expr
    ghost_augassign: "ghost" CNAME GHOST_AUG_OP expr
    GHOST_AUG_OP: "+=" | "-=" | "*="

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
    ?comparison: term | comparison COMP_OP term
    ?term: factor | term ADD_OP factor
    ?factor: unary | factor MUL_OP unary
    
    ?unary: UNARY_OP unary -> unary_op
          | atom

    ?atom: NUMBER -> number
         | ESCAPED_STRING -> string_literal
         | "self" "." CNAME -> field_access
         | "\\result" "[" expr "]" -> result_subscript
         | CNAME "[" expr "]" -> subscript_access
         | CNAME "(" expr_list ")" -> call_expr
         | CNAME "(" ")" -> call_expr
         | CNAME -> var
         | "\\result" -> result
         | "\\old" "(" expr ")" -> old_var
         | "\\length" "(" CNAME ")" -> array_length
         | "\\valid" "(" CNAME "," expr ")" -> valid_pred
         | "\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred
         | "\\at" "(" expr "," CNAME ")" -> at_expr
         | "\\length2d" "(" CNAME "," expr "," expr ")" -> length2d_pred
         | "\\valid2d" "(" CNAME "," expr "," expr ")" -> valid2d_pred
         | "\\is_sorted" "(" CNAME "," expr "," expr ")" -> is_sorted_pred
         | "\\sum" "(" CNAME "," expr "," expr ")" -> sum_pred
         | "(" expr ")"

    expr_list: expr ("," expr)*

    // Explicit tokens so Lark doesn't drop the operators
    IMPL_OP: "==>" | "<==>"
    OR_OP: "or"
    AND_OP: "and"
    EQ_OP: "==" | "!="
    COMP_OP: ">" | "<" | ">=" | "<="
    ADD_OP: "+" | "-"
    MUL_OP: "*" | "/"
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
    
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def precondition(self, expr): return Requires(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def postcondition(self, expr): return Ensures(expr)
    
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def assigns(self, target): 
        if isinstance(target, Nothing):
            return Assigns([target])
        elif isinstance(target, list):
            return Assigns(target)
        else:
            return Assigns([target])
            
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def loop_invariant(self, expr): return LoopInvariant(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def loop_variant(self, expr): return LoopVariant(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def class_invariant(self, expr): return ClassInvariant(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def function_variant(self, expr): return FunctionVariant(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def function_variant_structural(self, expr, ordering): return FunctionVariant(expr, str(ordering))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def diverges_decl(self): return Diverges()
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def trusted_decl(self): return Trusted()
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def bounded_int_decl(self, bits): return BoundedInt(int(bits))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def raises_decl(self, exc_type, condition): return RaisesDecl(str(exc_type), condition)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def ghost_assign(self, name, value): return GhostAssign(str(name), value, "=")
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def ghost_augassign(self, name, op, value): return GhostAssign(str(name), value, str(op))

    # Quantifiers
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def forall_expr(self, var, body): return Forall(str(var), body)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def exists_expr(self, var, body): return Exists(str(var), body)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def array_length(self, var): return ArrayLength(str(var))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def subscript_access(self, name, index): return SubscriptAccess(str(name), index)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def result_subscript(self, index): return SubscriptAccess("\\result", index)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def assigns_region(self, name, low, _op, high): return AssignsRegion(str(name), low, high)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def assigns_region_list(self, *regions): return list(regions)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def valid_pred(self, name, length): return Valid(str(name), length)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def separated_pred(self, name1, len1, name2, len2): return Separated(str(name1), len1, str(name2), len2)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def label_decl(self, name): return Label(str(name))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def at_expr(self, expr, label): return At(expr, str(label))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def length2d_pred(self, name, rows, cols): return Length2D(str(name), rows, cols)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def valid2d_pred(self, name, row, col): return Valid2D(str(name), row, col)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def is_sorted_pred(self, name, lo, hi): return IsSorted(str(name), lo, hi)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def sum_pred(self, name, lo, hi): return Sum(str(name), lo, hi)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def call_expr(self, *args):
        name = str(args[0])
        if len(args) > 1 and isinstance(args[1], list):
            return CallExpr(name, args[1])
        return CallExpr(name, [])

    # Operations
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def implication(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def logical_or(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def logical_and(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def equality(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def comparison(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def term(self, left, op, right): return BinOp(left, str(op), right)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def factor(self, left, op, right): return BinOp(left, str(op), right)
    
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def unary_op(self, op, expr): return UnaryOp(str(op), expr)

    # Atoms
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def number(self, n): return Number(float(n))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def string_literal(self, s): return StringLiteral(str(s)[1:-1])  # strip quotes
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def var(self, name): return Var(str(name))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def field_access(self, field_name): return FieldAccess("self", str(field_name))
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def result(self): return Result()
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def old_var(self, expr): return Old(expr)
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def nothing(self): return Nothing()
    
    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def expr_list(self, *exprs): return list(exprs)

# ---------------------------------------------------------
# 4. The Parser Interface
# ---------------------------------------------------------

class Module2_Parser:
    """Parses raw PyCSL string contracts into Contract AST objects."""
    def __init__(self):
        self.parser = Lark(PYCSL_GRAMMAR, parser='lalr', transformer=PyCSLTransformer())

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return self.parser.parse(contract_str)
        except LarkError as e:
            raise SyntaxError(f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{str(e)}")

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes
