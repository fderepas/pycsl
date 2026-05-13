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
class Result(CSLNode):
    pass

@dataclass
class Old(CSLNode):
    expr: CSLNode

@dataclass
class Nothing(CSLNode):
    pass

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

    precondition: "requires" expr
    postcondition: "ensures" expr
    
    // Extracted alias from group to prevent Lark GrammarError
    assigns: "assigns" assigns_target
    ?assigns_target: expr_list 
                   | "\\nothing" -> nothing

    loop_invariant: "loop" "invariant" expr
    loop_variant: "loop" "variant" expr

    // Expression hierarchy (handles operator precedence and left-recursion)
    ?expr: implication

    ?implication: logical_or | implication IMPL_OP logical_or
    ?logical_or: logical_and | logical_or OR_OP logical_and
    ?logical_and: equality | logical_and AND_OP equality
    ?equality: comparison | equality EQ_OP comparison
    ?comparison: term | comparison COMP_OP term
    ?term: factor | term ADD_OP factor
    ?factor: unary | factor MUL_OP unary
    
    ?unary: UNARY_OP unary -> unary_op
          | atom

    ?atom: NUMBER -> number
         | CNAME -> var
         | "\\result" -> result
         | "\\old" "(" expr ")" -> old_var
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

    %import common.CNAME
    %import common.NUMBER
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
    def var(self, name): return Var(str(name))
    def result(self): return Result()
    def old_var(self, expr): return Old(expr)
    def nothing(self): return Nothing()
    
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
