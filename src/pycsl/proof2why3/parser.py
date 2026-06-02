"""Unified type-expression parser for Rocq, Lean, and WhyML axiom
bodies (proof2why3 Phases 1+2+3 v1 — sticky-01.md).

After Unicode + library-prefix normalization, all three input
languages reduce to a small first-order surface that this single
recursive-descent parser handles:

    expr   := quant
            | implication
    quant  := 'forall' var+ ':' ty ',' expr
            | 'exists' var+ ':' ty ',' expr
    implication := disjunction ('->' implication)?
    disjunction := conjunction ('\\/' conjunction)*
    conjunction := comparison  ('/\\' comparison)*
    comparison  := arith (('='|'>='|'<='|'>'|'<'|'<>'|'!=') arith)?
    arith       := factor (('+'|'-') factor)*
    factor      := atom (('*'|'mod') atom)*
    atom        := number
                 | '(' expr ')'
                 | 'not' atom
                 | ident (atom)*

(`mod` is treated as a multiplicative-precedence infix here — matches
what Coq's pretty-printer + our prefix-strip phase produces.)

The same parser consumes:
- Coq's `Check` output after PeanoNat.Nat.gcd → gcd / forall (a b :
  nat) → forall a b : nat prefix-strip and binder normalization.
- Lean's `#check` output after ∀ → forall, ≥ → >=, Nat.gcd → gcd,
  a.gcd b → gcd a b dot-notation expansion.
- The Module 6 _AXIOM_REGISTRY bodies.

Production gap vs sertop / Lean-Elab:
- Implicit-argument insertion (e.g. `@gcd Nat _` in Lean) is not
  recognized; we strip leading `@` heuristically.
- Type ascriptions inside expressions are dropped.
- Coq's universe polymorphism + Lean's universe stratification are
  ignored entirely.

For the gcd theorem family the parser is exhaustive over the actual
shapes coqc/lake emit.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from proof2why3.ir import (
    App, BinOp, BoolLit, Exists, Forall, IntLit, Term, UnaryOp, Unsupported,
    Var, mk_arrow_chain,
)


# ---------------------------------------------------------------------------
# Pre-parse normalization: prover-specific text → unified surface
# ---------------------------------------------------------------------------


_UNICODE_OPS = {
    "∀":   "forall ",
    "∃":   "exists ",
    "→":   "->",
    "≥":   ">=",
    "≤":   "<=",
    "∨":   r"\/",
    "∧":   r"/\\",
    "≠":   "<>",
    "¬":   " not ",
    "≡":   "=",
}

_LIBRARY_PREFIX_STRIPS: List[Tuple[str, str]] = [
    ("PeanoNat.Nat.gcd",    "gcd"),
    ("PeanoNat.Nat.modulo", "mod"),
    ("PeanoNat.Nat.add",    "add"),
    ("PeanoNat.Nat.mul",    "mul"),
    ("PeanoNat.Nat.sub",    "sub"),
    ("Nat.gcd",             "gcd"),
    ("Nat.modulo",          "mod"),
    ("Nat.mod",             "mod"),
    ("Nat.add",             "add"),
    ("Nat.mul",             "mul"),
    ("Nat.sub",             "sub"),
    ("BinNat.N.gcd",        "gcd"),
    ("BinNat.N.modulo",     "mod"),
    # PyCSL formal-semantics inductives — instance signatures in
    # `PyCSL.AST.instDecidableEqExpr` print as `DecidableEq
    # PyCSL.AST.Expr`; strip the namespace so the canonical form is
    # `DecidableEq Expr`, paralleling the `Nat.gcd → gcd` pattern.
    ("PyCSL.AST.Expr",      "Expr"),
]


def normalize_surface(s: str) -> str:
    """Apply Unicode + library-prefix + dot-notation rewrites so the
    string matches the parser's surface grammar.

    Idempotent: a second call returns the same string."""
    out = s.strip()
    for u, a in _UNICODE_OPS.items():
        out = out.replace(u, a)
    for src, dst in _LIBRARY_PREFIX_STRIPS:
        out = out.replace(src, dst)
    # Lean dot notation `a.gcd b` → `gcd a b` (also `a.mod b`, etc.).
    for fn in ("gcd", "mod", "add", "mul", "sub"):
        out = re.sub(
            rf"\b([a-zA-Z_][a-zA-Z0-9_]*)\.{fn}\b",
            rf"{fn} \1", out,
        )
    # Lean `%` infix → `mod` infix (parser handles `mod` at factor level).
    out = re.sub(
        r"([\w\d])\s*%\s*([\w\d])",
        r"\1 mod \2", out,
    )
    # Strip leading `@` (Lean's explicit-binder notation).
    out = re.sub(r"@(\w)", r"\1", out)
    # Multi-paren binders: `forall (a b : ty) (c : ty2) ..., body` →
    # `forall a b : ty, forall c : ty2, ..., body` — sequential foralls
    # the parser handles via the repeated quant rule. Applied as a
    # fixpoint so any number of paren groups is flattened.
    prev = None
    while prev != out:
        prev = out
        out = re.sub(
            r"\bforall\s*\(\s*([^()]+?)\s*\)\s*\(",
            r"forall \1, forall (",
            out,
        )
    # Final / single paren group: `forall (a b : ty),` → `forall a b : ty,`.
    out = re.sub(
        r"\bforall\s*\(\s*([^()]+?)\s*\)\s*,",
        r"forall \1,",
        out,
    )
    out = re.sub(r"\s+", " ", out).strip()
    return out


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------


@dataclass
class Token:
    kind: str   # 'IDENT', 'INT', 'OP', 'LPAREN', 'RPAREN', 'COMMA', 'COLON'
    value: str

    def __repr__(self) -> str:
        return f"{self.kind}({self.value!r})"


# Multi-char operators must be tried longest-first.
_OP_TOKENS = [
    "->", ">=", "<=", "<>", "==", "!=",
    r"\/", r"/\\", "=", ">", "<", "+", "-", "*",
]


def lex(s: str) -> List[Token]:
    """Tokenize a normalized type expression. Whitespace is ignored;
    punctuation is single-char; operators are multi-char per
    `_OP_TOKENS`."""
    toks: List[Token] = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == "(":
            toks.append(Token("LPAREN", "("))
            i += 1
            continue
        if c == ")":
            toks.append(Token("RPAREN", ")"))
            i += 1
            continue
        if c == ",":
            toks.append(Token("COMMA", ","))
            i += 1
            continue
        if c == ":":
            toks.append(Token("COLON", ":"))
            i += 1
            continue
        # Try multi-char operators (longest first).
        matched = False
        for op in _OP_TOKENS:
            if s.startswith(op, i):
                toks.append(Token("OP", op))
                i += len(op)
                matched = True
                break
        if matched:
            continue
        # Integer literal.
        if c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            toks.append(Token("INT", s[i:j]))
            i = j
            continue
        # Identifier (alphanumeric, underscore, dot for dotted names like
        # leftover library refs; we treat them as opaque idents).
        if c.isalpha() or c == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] in "_'"):
                j += 1
            toks.append(Token("IDENT", s[i:j]))
            i = j
            continue
        # Unknown char — skip with a warning.
        toks.append(Token("OP", c))
        i += 1
    return toks


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------


# Operator precedence layers (lowest to highest).
_LOGICAL_DISJ_OPS = {r"\/"}
_LOGICAL_CONJ_OPS = {r"/\\"}
_COMPARISON_OPS = {"=", ">=", "<=", ">", "<", "<>", "!=", "=="}
_ARITH_ADD_OPS = {"+", "-"}
_ARITH_MUL_OPS = {"*"}      # `mod` handled separately as identifier-infix


# Known prefix function heads in our IR. Anything not in this set is
# still a valid App head; the list is used only by the precedence
# logic that decides whether `mod` is a binary operator or a unary
# function name.
_KNOWN_FN_HEADS = {"gcd", "mod", "add", "mul", "sub", "DecidableEq",
                   # UnixInodeFileSystem witness symbols (match the
                   # registry symbol names so the round-trip / bitwise
                   # statements parse as applications).
                   "bit_and",
                   "struct_pack_i1a1", "struct_unpack_i1a1",
                   "struct_pack_i2", "struct_unpack_i2",
                   "struct_pack_i18", "struct_unpack_i18"}


class _Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.toks = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Optional[Token]:
        idx = self.pos + offset
        if idx < len(self.toks):
            return self.toks[idx]
        return None

    def take(self) -> Token:
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def expect(self, kind: str, value: Optional[str] = None) -> Token:
        t = self.peek()
        if t is None or t.kind != kind or (value is not None and t.value != value):
            raise SyntaxError(
                f"expected {kind}({value}) at pos {self.pos}, got {t}"
            )
        return self.take()

    # expr → quant | implication
    def parse_expr(self) -> Term:
        t = self.peek()
        if t is not None and t.kind == "IDENT" and t.value in ("forall", "exists"):
            return self.parse_quant()
        return self.parse_implication()

    def parse_quant(self) -> Term:
        kind_tok = self.take()
        # Collect binder names until `:`.
        binders: List[str] = []
        while True:
            t = self.peek()
            if t is None:
                raise SyntaxError("unexpected EOF in quantifier binders")
            if t.kind == "COLON":
                break
            if t.kind == "IDENT":
                binders.append(self.take().value)
            else:
                raise SyntaxError(f"unexpected token {t} in quantifier binders")
        self.expect("COLON")
        # The binder type may be multiple tokens (`list Z`, `array int`,
        # `List Int`); consume IDENTs up to the COMMA and join them.
        ty_parts: List[str] = []
        while True:
            t = self.peek()
            if t is None:
                raise SyntaxError("unexpected EOF in quantifier type")
            if t.kind == "COMMA":
                break
            if t.kind == "IDENT":
                ty_parts.append(self.take().value)
            else:
                raise SyntaxError(f"unexpected token {t} in quantifier type")
        ty = " ".join(ty_parts)
        self.expect("COMMA")
        body = self.parse_expr()
        if kind_tok.value == "forall":
            return Forall(binders=tuple(binders), ty=ty, body=body)
        return Exists(binders=tuple(binders), ty=ty, body=body)

    def parse_implication(self) -> Term:
        lhs = self.parse_disjunction()
        t = self.peek()
        if t is not None and t.kind == "OP" and t.value == "->":
            self.take()
            rhs = self.parse_implication()  # right-associative
            return BinOp("->", lhs, rhs)
        return lhs

    def parse_disjunction(self) -> Term:
        out = self.parse_conjunction()
        while True:
            t = self.peek()
            if t is None or t.kind != "OP" or t.value not in _LOGICAL_DISJ_OPS:
                break
            op = self.take().value
            rhs = self.parse_conjunction()
            out = BinOp(op, out, rhs)
        return out

    def parse_conjunction(self) -> Term:
        out = self.parse_comparison()
        while True:
            t = self.peek()
            if t is None or t.kind != "OP" or t.value not in _LOGICAL_CONJ_OPS:
                break
            op = self.take().value
            rhs = self.parse_comparison()
            out = BinOp(op, out, rhs)
        return out

    def parse_comparison(self) -> Term:
        lhs = self.parse_arith_add()
        t = self.peek()
        if t is not None and t.kind == "OP" and t.value in _COMPARISON_OPS:
            op = self.take().value
            mid = self.parse_arith_add()
            # Chained comparison `a <= b < c` (Coq's `0 <= x < 2`
            # notation) desugars to `(a <= b) /\ (b < c)` to match the
            # registry's explicit conjunction.
            t2 = self.peek()
            if t2 is not None and t2.kind == "OP" and t2.value in _COMPARISON_OPS:
                op2 = self.take().value
                rhs = self.parse_arith_add()
                return BinOp(r"/\\", BinOp(op, lhs, mid), BinOp(op2, mid, rhs))
            return BinOp(op, lhs, mid)
        return lhs

    def parse_arith_add(self) -> Term:
        out = self.parse_arith_mul()
        while True:
            t = self.peek()
            if t is None or t.kind != "OP" or t.value not in _ARITH_ADD_OPS:
                break
            op = self.take().value
            rhs = self.parse_arith_mul()
            out = BinOp(op, out, rhs)
        return out

    def parse_arith_mul(self) -> Term:
        out = self.parse_atom_application()
        while True:
            t = self.peek()
            if t is None:
                break
            if t.kind == "OP" and t.value in _ARITH_MUL_OPS:
                op = self.take().value
                rhs = self.parse_atom_application()
                out = BinOp(op, out, rhs)
                continue
            # `mod` as identifier-infix (Lean-style `a mod b` after
            # `%` → `mod` normalization). Folded into App(mod, ...)
            # for shape parity with Rocq's `mod a b` prefix form.
            if t.kind == "IDENT" and t.value == "mod":
                self.take()
                rhs = self.parse_atom_application()
                out = App(head="mod", args=(out, rhs))
                continue
            break
        return out

    def parse_atom_application(self) -> Term:
        atom = self.parse_atom()
        # If atom is a Var with name in _KNOWN_FN_HEADS, greedily
        # gather following atoms as args (curried application).
        if isinstance(atom, Var) and atom.name in _KNOWN_FN_HEADS:
            args: List[Term] = []
            while True:
                t = self.peek()
                if t is None:
                    break
                if t.kind == "IDENT":
                    # Heuristic: if the next IDENT is a known function head, it's a separate
                    # application chain — but in our pretty-print we always parenthesize,
                    # so this case shouldn't fire mid-application.
                    args.append(self.parse_atom())
                    continue
                if t.kind == "INT":
                    args.append(self.parse_atom())
                    continue
                if t.kind == "LPAREN":
                    args.append(self.parse_atom())
                    continue
                break
            return App(head=atom.name, args=tuple(args))
        return atom

    def parse_atom(self) -> Term:
        t = self.peek()
        if t is None:
            raise SyntaxError("unexpected EOF in atom")
        if t.kind == "INT":
            self.take()
            return IntLit(int(t.value))
        if t.kind == "LPAREN":
            self.take()
            inner = self.parse_expr()
            # Tuple literal: `(a, b, ...)` → App("tuple", [a, b, ...]).
            if self.peek() is not None and self.peek().kind == "COMMA":
                elts = [inner]
                while self.peek() is not None and self.peek().kind == "COMMA":
                    self.take()
                    elts.append(self.parse_expr())
                self.expect("RPAREN")
                return App(head="tuple", args=tuple(elts))
            self.expect("RPAREN")
            return inner
        if t.kind == "IDENT":
            ident = self.take().value
            if ident == "true":
                return BoolLit(True)
            if ident == "false":
                return BoolLit(False)
            if ident == "not":
                arg = self.parse_atom()
                return UnaryOp("not", arg)
            return Var(name=ident)
        if t.kind == "OP" and t.value == "-":
            self.take()
            arg = self.parse_atom()
            return UnaryOp("-", arg)
        raise SyntaxError(f"parse_atom: unexpected {t}")


def parse_type_expr(s: str) -> Term:
    """High-level entry: normalize + lex + parse + return Term."""
    if not s.strip():
        return Unsupported(reason="empty", raw=s)
    normalized = normalize_surface(s)
    tokens = lex(normalized)
    if not tokens:
        return Unsupported(reason="empty after normalize", raw=s)
    p = _Parser(tokens)
    try:
        out = p.parse_expr()
        if p.pos != len(p.toks):
            # Trailing tokens — not a clean parse.
            return Unsupported(
                reason=f"trailing tokens at {p.pos}: {p.toks[p.pos:]}",
                raw=s,
            )
        return out
    except (SyntaxError, IndexError) as exc:
        return Unsupported(reason=str(exc), raw=s)
