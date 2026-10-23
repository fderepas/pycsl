r"""Test 0935 — CLASS construction of an AST node lowers to the `emit_ir` ADT CONSTRUCTOR
(NODE-CTOR), and an ADT-returning same-class sibling call binds CONCRETELY.

Before this capability a recursive-descent precedence chain could not be verified at all,
for two independent reasons.

1. NODE-CTOR.  The emitter already lowered the DICT form of an IR-node construction

       {"type": "BinOp", "op": o, "left": l, "right": r}   ->   (IrBinOp o l r)

   but the CLASS form of the SAME node — which is what a parser actually writes —

       BinOp(l, o, r)

   fell through to `_call_record_constructor` and became a `binop` RECORD literal
   `{ binop_left = l; binop_op = o; binop_right = r }`.  A record literal has a different
   WhyML type from the `emit_ir` sum, so the moment the value flowed into an
   `emit_ir`-typed position (a `-> "ExprIR"` return, a sibling's argument, the `left`
   accumulator of the next precedence level) the file failed to type-check:

       This expression has type PyCSL_Program.binop, but is expected to have type
       PyCSL_Program.emit_ir

   Now `BinOp(l, o, r)` lowers to `(IrBinOp o l r)` — the SAME constructor the dict form
   reaches, through the SAME `_IRNODE_CTORS` table.

2. ADT-RETURNING SIBLING CALL.  The concrete same-class sibling call
   (`self.<m>(...)` -> `(<cls>__<m> self …)`) was gated on a RECORD return.  An
   `emit_ir`-returning sibling therefore degraded to a fresh, UNCONSTRAINED abstract

       val self__parse_atom_0 (self: parser) : emit_ir      (* no ensures at all *)

   — and a varargs guard degraded further, to a RECEIVER-LESS

       val self_at_op_1 (x0: seq string) : int

   which cannot see `self` at all, so the loop guard had no relation whatsoever to the
   token cursor.  Both now bind to the real, verified definitions.

ANTI-FACADE — machine-enforced, three ways.

  * The ctor payload is bound BY NAME, never by position: the class's positional
    `__init__` params name the actuals and `_IRNODE_CTORS["BinOp"]`'s payload list names
    the ctor's argument order (`op, left, right` — deliberately NOT the class's field
    order `left, op, right`).  If ANY payload slot is unbound the lowering DECLINES
    rather than dropping a child.  Swapping `BinOp(left, op, right)` to
    `BinOp(right, op, left)` in `parse_term` below changes the emitted WhyML from
    `(IrBinOp !op !left …)` to `(IrBinOp !op … !left)` — the mutation is visible, so the
    children cannot have been erased.
  * There is no `isinstance_op 0 0`, no int-hash key, and no receiver-less `val`: every
    call in `parse_term`/`parse_factor` below emits as `(parser__<m> self …)` against a
    definition proved in this same file.
  * With the old lowering this file does not TYPE-CHECK, so a dropped or int-erased node
    child is a hard L3-tc failure, not a silent green.

NON-VACUITY — falsifiable VCs.  `parse_factor` and `parse_term` each carry the two-sided
frame control `self.i >= \old(self.i)`.  It is provable ONLY because the concrete
`advance` really is the thing that moves the cursor; with the old receiver-less
`val self_advance_0 ()` stub the cursor motion was invisible and the clause could not be
related to the body at all.  `cur`'s array read carries a genuine `index in array bounds`
obligation discharged by the class invariant.

TERMINATION BOUNDARY (why this fixture is loop-free).  The live precedence chain uses
`while self.at_op(...)`, not `if`.  That loop's termination VC is NOT dischargeable with
today's contract grammar: `advance` only increments the cursor while `self.i <
len(self.toks) - 1`, so the measure `\length(self.toks) - self.i` stops decreasing at the
last index, and the loop terminates in reality only because the lexer appends an EOF
sentinel token whose kind is never an operator.  Stating that needs the class invariant

    #@ class invariant self.toks[\length(self.toks) - 1].py_type == "EOF"

— a `.field` projection off a SELF-FIELD subscript, which the contract grammar REJECTS
("unexpected trailing input (got OP '.')"), while the sibling forms `<name>[i].<field>`
and `\result[i].<field>` are both accepted (the former then lowers to an unbound
`subscript_get` in a class-invariant context).  Closing that asymmetry is the prerequisite
for converting the loop-carrying precedence levels; this fixture pins the node-construction
and sibling-binding halves, which are independent of it.

No new axiom, no new abstract val.
"""
from typing import List


def mutable_state(cls):
    return cls


class Tok:
    def __init__(self, py_type, string):
        self.py_type: str = py_type
        self.string: str = string


class Var:
    def __init__(self, name):
        self.name: str = name


class BinOp:
    # field order `left, op, right`; the ADT ctor's payload order is `op, left, right`
    def __init__(self, left, op, right):
        self.left: "ExprIR" = left
        self.op: str = op
        self.right: "ExprIR" = right


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def cur(self) -> Tok:
        return self.toks[self.i]

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ ensures self.i <= \old(self.i) + 1
    #@ assigns self.i
    def advance(self) -> Tok:
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    # VARARGS guard — the shape that used to emit a receiver-less `val self_at_op_1`.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_op(self, *vals: str) -> bool:
        t = self.cur()
        return t.py_type == "OP" and (not vals or t.string in vals)

    # LEAF: a class construction in an `emit_ir`-typed return position.
    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def parse_atom(self) -> "ExprIR":
        name = self.advance().string
        return Var(name)

    # ONE precedence level, LOOP-FREE (see the TERMINATION BOUNDARY note above): an
    # ADT-returning sibling call in both operand positions + a node construction whose
    # children are BOTH `emit_ir` values, under a real varargs guard.
    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def parse_factor(self) -> "ExprIR":
        left = self.parse_atom()
        if self.at_op("*", "/"):
            op = self.advance().string
            return BinOp(left, op, self.parse_atom())
        return left

    # A SECOND level, delegating to the first — the precedence-chain shape itself.
    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def parse_term(self) -> "ExprIR":
        left = self.parse_factor()
        if self.at_op("+", "-"):
            op = self.advance().string
            return BinOp(left, op, self.parse_factor())
        return left


if __name__ == "__main__":
    p = Parser([Tok("NAME", "a"), Tok("OP", "+"), Tok("NAME", "b")])
    assert p.parse_term() is not None
