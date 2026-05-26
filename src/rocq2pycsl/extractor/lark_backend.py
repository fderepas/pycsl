"""Lark-based extractor for the supported Gallina subset.

Default backend for rocq2pycsl. No opam dependencies — parses the `.v`
file at the surface level.

Pipeline:

  1. `lex.strip_comments` removes `(* ... *)` blocks.
  2. `lex.split_vernacs` splits the file into top-level commands.
  3. `_match_vernac_head` regex-classifies each command
     (Theorem/Lemma/Definition/Fixpoint/Function/ignored).
  4. Expression bodies are parsed by the Lark grammar
     (`gallina_grammar.lark`).
  5. `_AstBuilder` lowers the parse tree into the surface Gallina AST
     defined in `gallina.py`.

Anything we don't recognize at the top level is silently ignored
(common for `Require`, `Import`, `Open Scope`, etc.). Anything we
recognize but can't translate inside an expression becomes a
`GUnsupported` node with a useful reason.
"""

from __future__ import annotations

import re
from pathlib import Path

from lark import Lark, Token, Transformer, UnexpectedInput, v_args

from .gallina import (
    GApp,
    GBinOp,
    GDivides,
    GExists,
    GForall,
    GFunctionDef,
    GLit,
    GTheorem,
    GUnaryOp,
    GUnsupported,
    GVar,
    GallinaModule,
    GallinaNode,
)
from .lex import Vernac, split_vernacs, strip_comments


_GRAMMAR_PATH = Path(__file__).with_name("gallina_grammar.lark")
_PARSER = Lark.open(_GRAMMAR_PATH, parser="lalr", maybe_placeholders=False)


# ──────────────────────────────────────────────────────────────────────
# Top-level vernac dispatcher
# ──────────────────────────────────────────────────────────────────────


# Identifier pattern matching Coq's CNAME (includes apostrophes for
# things like `gcd'` and `Foo.bar.baz` qualified names).
_ID = r"[A-Za-z_][A-Za-z_0-9']*"

# These map to GTheorem (we treat them all as "trusted oracle" statements).
_THEOREM_HEAD = re.compile(
    rf"^(?:Theorem|Lemma|Proposition|Corollary|Fact|Remark)\s+({_ID})\s*:\s*(.*?)\s*$",
    re.DOTALL,
)

# Definition / Fixpoint / Function. We capture the head + (optional)
# binder block + (optional) measure block + (optional) return type +
# body — but in v1 the body is *ignored*; we only need the signature
# and termination annotation.
_DEFINITION_HEAD = re.compile(
    rf"^(Definition|Fixpoint|Function)\s+({_ID})\s*(.*?)\s*:=\s*.*$",
    re.DOTALL,
)

_PROOF_KEYWORDS = frozenset({
    "Proof", "Qed", "Defined", "Admitted", "Abort", "Save", "End", "Hint",
})


def parse_module(text: str, *, source_path: str = "") -> GallinaModule:
    """Top-level entry point. Returns the populated GallinaModule."""
    text = strip_comments(text)
    vernacs = split_vernacs(text)

    theorems: list[GTheorem] = []
    functions: list[GFunctionDef] = []

    for v in vernacs:
        head_word = v.body.split(None, 1)[0] if v.body else ""
        if head_word in _PROOF_KEYWORDS:
            # Proof bodies and section closers are skipped entirely.
            continue

        thm = _maybe_theorem(v)
        if thm is not None:
            theorems.append(thm)
            continue

        fn = _maybe_function_def(v)
        if fn is not None:
            functions.append(fn)
            continue
        # Unrecognized at the top level — Require, Import, Open Scope,
        # Inductive, Notation, etc. Silently ignored.

    return GallinaModule(
        theorems=tuple(theorems),
        functions=tuple(functions),
        source_path=source_path,
    )


def _maybe_theorem(v: Vernac) -> GTheorem | None:
    m = _THEOREM_HEAD.match(v.body)
    if not m:
        return None
    name, statement_text = m.group(1), m.group(2).strip()
    binders, body = _split_outer_binders(statement_text)
    statement_node = _parse_expr(body, v.line)
    return GTheorem(
        name=name,
        binders=tuple(binders),
        statement=statement_node,
        source_line=v.line,
    )


def _maybe_function_def(v: Vernac) -> GFunctionDef | None:
    m = _DEFINITION_HEAD.match(v.body)
    if not m:
        return None
    keyword, name, sig = m.group(1), m.group(2), m.group(3).strip()

    # The signature is everything between the name and `:=`. It contains
    # binders, an optional `{measure ...}`, and an optional `: return_ty`.
    params, measure_node, return_ty = _parse_def_signature(sig, v.line)
    return GFunctionDef(
        name=name,
        params=tuple(params),
        return_ty=return_ty,
        measure=measure_node,
        is_recursive=keyword in {"Fixpoint", "Function"},
        source_line=v.line,
    )


# ──────────────────────────────────────────────────────────────────────
# Binder helpers
# ──────────────────────────────────────────────────────────────────────


def _split_outer_binders(stmt: str) -> tuple[list[tuple[str, str]], str]:
    """If `stmt` begins with `forall <binders>,` peel them off.

    Returns (binder_list, body_text). The translator decides which
    prefix to absorb into the target function's parameter scope.
    """
    stripped = stmt.lstrip()
    if not stripped.startswith("forall"):
        return [], stmt
    # Use the Lark parser as an oracle: parse the whole statement, then
    # walk down the outer Forall chain unwinding binders. This keeps the
    # binder-parsing logic in one place (the grammar).
    parsed = _parse_expr(stmt, line=0)
    binders: list[tuple[str, str]] = []
    cur = parsed
    while isinstance(cur, GForall):
        binders.append((cur.var, cur.ty))
        cur = cur.body
    return binders, _unparse(cur)


def _parse_def_signature(
    sig: str, line: int
) -> tuple[list[tuple[str, str]], GallinaNode | None, str]:
    """Pick apart `(a b : nat) {measure n} : nat` style signatures.

    Returns (params, measure_expr, return_type). Anything we don't
    recognize is left in `params` as a best effort or recorded as a
    failure for the caller.
    """
    measure: GallinaNode | None = None

    # Pull out a `{measure <expr> <var>?}` block if present.
    measure_match = re.search(r"\{\s*measure\s+(.*?)\s*\}", sig, flags=re.DOTALL)
    if measure_match:
        measure_body = measure_match.group(1)
        # `{measure (fun n => n) b}` — strip the trailing var if any so
        # we only parse the measure expression itself.
        toks = measure_body.rsplit(None, 1)
        if len(toks) == 2 and re.fullmatch(_ID, toks[1]):
            measure_body = toks[0]
        try:
            measure = _parse_expr(measure_body, line)
        except ValueError:
            measure = GUnsupported(
                reason="failed to parse {measure ...} expression",
                raw=measure_body,
            )
        sig = sig[: measure_match.start()] + sig[measure_match.end() :]

    # Split on the first top-level `:` (outside any parens). The left
    # side is the binder list; the right is the return type. We can't
    # just match ` : ` with regex because `(n : nat)` contains an inner
    # colon that should NOT split the signature.
    split_at = _find_top_level_colon(sig)
    if split_at is not None:
        binder_part = sig[:split_at].strip()
        return_ty = sig[split_at + 1 :].strip()
    else:
        binder_part = sig.strip()
        return_ty = "_"  # unknown — Coq inferred it

    params = _parse_def_binders(binder_part)
    return params, measure, return_ty


def _find_top_level_colon(s: str) -> int | None:
    """Index of the first `:` at paren-depth 0, or None.

    Required because `Definition succ (n : nat) : nat := ...` contains
    two colons; only the second separates binders from the return type.
    """
    depth = 0
    for i, ch in enumerate(s):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0:
            return i
    return None


_GROUP_BINDER = re.compile(rf"\(\s*((?:{_ID}\s*)+):\s*([^)]+?)\s*\)")


def _parse_def_binders(text: str) -> list[tuple[str, str]]:
    """Parse parenthesized typed-binder groups: `(a b : nat) (c : Z)`.

    Untyped/loose binders aren't supported in this v1 path — Definition
    arguments usually carry explicit types.
    """
    out: list[tuple[str, str]] = []
    for m in _GROUP_BINDER.finditer(text):
        names = m.group(1).split()
        ty = m.group(2).strip()
        for n in names:
            out.append((n, ty))
    return out


# ──────────────────────────────────────────────────────────────────────
# Expression parsing
# ──────────────────────────────────────────────────────────────────────


def _parse_expr(text: str, line: int) -> GallinaNode:
    try:
        tree = _PARSER.parse(text)
    except UnexpectedInput as e:
        raise ValueError(
            f"failed to parse expression at line {line}: {e}\n"
            f"  source: {text!r}"
        ) from e
    return _AstBuilder().transform(tree)


def _unparse(node: GallinaNode) -> str:
    """Re-emit a Gallina expression text for re-parsing.

    Only used after binder peeling, so we can keep the rest of the
    statement as text and feed it back through the parser. This is a
    minimal pretty-printer — round-trip fidelity is not required, just
    re-parseability for the unbound remainder.
    """
    if isinstance(node, GVar):
        return node.name
    if isinstance(node, GLit):
        return str(node.value)
    if isinstance(node, GApp):
        return "(" + node.fn + " " + " ".join(_unparse(a) for a in node.args) + ")"
    if isinstance(node, GBinOp):
        return f"({_unparse(node.lhs)} {node.op} {_unparse(node.rhs)})"
    if isinstance(node, GUnaryOp):
        return f"({node.op} {_unparse(node.arg)})"
    if isinstance(node, GForall):
        return f"forall {node.var} : {node.ty}, {_unparse(node.body)}"
    if isinstance(node, GExists):
        return f"exists {node.var} : {node.ty}, {_unparse(node.body)}"
    if isinstance(node, GDivides):
        return f"({_unparse(node.d)} | {_unparse(node.n)})"
    if isinstance(node, GUnsupported):
        return f"<unsupported: {node.reason}>"
    raise TypeError(f"_unparse: unknown node {type(node).__name__}")


# ──────────────────────────────────────────────────────────────────────
# Lark → Gallina AST
# ──────────────────────────────────────────────────────────────────────


@v_args(inline=True)
class _AstBuilder(Transformer):
    """Lower the Lark parse tree into surface Gallina AST nodes."""

    # ── terminals / atoms ──────────────────────────────────────────────

    def number(self, tok: Token) -> GLit:
        return GLit(int(tok))

    def var(self, qident: str) -> GVar | GLit:
        # `True`/`False` are parsed as identifiers; promote them here.
        if qident == "True":
            return GVar("True")
        if qident == "False":
            return GVar("False")
        return GVar(qident)

    def qident(self, *parts: Token) -> str:
        return ".".join(str(p) for p in parts)

    def type_expr(self, ty: str) -> str:
        return ty

    def ty_arrow(self, *parts: str) -> str:
        # `parts` is either (lhs,) or (lhs, rhs) — Lark elides the literal arrow.
        return " -> ".join(p for p in parts)

    def ty_prod(self, *parts) -> str:
        # parts is interleaved: type_app, MUL_OP, type_app, MUL_OP, ...
        # Filter to just the type fragments.
        return " * ".join(p for p in parts if not isinstance(p, Token))

    def type_app(self, head: str, *args: str) -> str:
        if not args:
            return head
        return head + " " + " ".join(args)

    def ty_arg_qident(self, name: str) -> str:
        return name

    def ty_arg_number(self, tok: Token) -> str:
        return str(tok)

    def ty_arg_paren(self, inner: str) -> str:
        return f"({inner})"

    # ── binders ────────────────────────────────────────────────────────

    def typed_group_binder(self, *items) -> list[tuple[str, str]]:
        # items = [IDENT, IDENT, ..., type_str]
        *names, ty = items
        return [(str(n), ty) for n in names]

    def typed_loose_binder(self, *items) -> list[tuple[str, str]]:
        *names, ty = items
        return [(str(n), ty) for n in names]

    def bare_binder(self, *names: Token) -> list[tuple[str, str]]:
        return [(str(n), "_") for n in names]

    def binders(self, *groups) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for g in groups:
            out.extend(g)
        return out

    # ── parenthesized / divides ────────────────────────────────────────

    def paren_or_divides(self, *parts) -> GallinaNode:
        # Either (expr,) for plain parens, or (lhs, PIPE_TOK, rhs) for divides.
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 3 and isinstance(parts[1], Token) and parts[1].type == "DIVIDES_PIPE":
            return GDivides(d=parts[0], n=parts[2])
        # Lark may pass the PIPE token as part of `parts` differently
        # depending on `inline`. Fall back to a defensive search.
        non_tokens = [p for p in parts if not isinstance(p, Token)]
        if len(non_tokens) == 2:
            return GDivides(d=non_tokens[0], n=non_tokens[1])
        return non_tokens[0]

    # ── application ────────────────────────────────────────────────────

    def app_chain(self, head: GallinaNode, *args: GallinaNode) -> GallinaNode:
        if not args:
            return head
        if isinstance(head, GVar):
            return GApp(fn=head.name, args=tuple(args))
        # Higher-order application (the head is itself a compound expr) —
        # not in the v1 supported subset.
        return GUnsupported(
            reason="higher-order application",
            raw=str(head),
        )

    # ── arithmetic chains ─────────────────────────────────────────────

    def add_chain(self, first: GallinaNode, *rest) -> GallinaNode:
        return _left_assoc_chain(first, rest)

    def mul_chain(self, first: GallinaNode, *rest) -> GallinaNode:
        return _left_assoc_chain(first, rest)

    def neg(self, operand: GallinaNode) -> GUnaryOp:
        return GUnaryOp(op="-", arg=operand)

    # ── comparisons ────────────────────────────────────────────────────

    def cmp(self, lhs: GallinaNode, *rest) -> GallinaNode:
        if not rest:
            return lhs
        op_tok, rhs = rest
        return GBinOp(op=str(op_tok), lhs=lhs, rhs=rhs)

    # ── logical ────────────────────────────────────────────────────────

    def negation(self, operand: GallinaNode) -> GUnaryOp:
        return GUnaryOp(op="~", arg=operand)

    def andexp(self, lhs: GallinaNode, *rest) -> GallinaNode:
        if not rest:
            return lhs
        rhs, = rest
        return GBinOp(op="/\\", lhs=lhs, rhs=rhs)

    def orexp(self, lhs: GallinaNode, *rest) -> GallinaNode:
        if not rest:
            return lhs
        rhs, = rest
        return GBinOp(op="\\/", lhs=lhs, rhs=rhs)

    def impl(self, lhs: GallinaNode, *rest) -> GallinaNode:
        if not rest:
            return lhs
        rhs, = rest
        return GBinOp(op="->", lhs=lhs, rhs=rhs)

    def iff(self, lhs: GallinaNode, *rest) -> GallinaNode:
        if not rest:
            return lhs
        rhs, = rest
        return GBinOp(op="<->", lhs=lhs, rhs=rhs)

    # ── quantifiers ────────────────────────────────────────────────────

    def forall_expr(self, binders: list[tuple[str, str]], body: GallinaNode) -> GallinaNode:
        node = body
        for var, ty in reversed(binders):
            node = GForall(var=var, ty=ty, body=node)
        return node

    def exists_expr(self, binders: list[tuple[str, str]], body: GallinaNode) -> GallinaNode:
        node = body
        for var, ty in reversed(binders):
            node = GExists(var=var, ty=ty, body=node)
        return node

    # ── start ──────────────────────────────────────────────────────────

    def start(self, expr: GallinaNode) -> GallinaNode:
        return expr


def _left_assoc_chain(first: GallinaNode, rest: tuple) -> GallinaNode:
    """Build a left-associative chain from `[op0, rhs0, op1, rhs1, ...]`."""
    cur = first
    it = iter(rest)
    for op_tok in it:
        rhs = next(it)
        cur = GBinOp(op=str(op_tok), lhs=cur, rhs=rhs)
    return cur
