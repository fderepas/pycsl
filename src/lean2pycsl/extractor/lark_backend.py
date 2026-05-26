"""Lark-based extractor for the supported Lean 4 subset.

Default backend for lean2pycsl. No `lake` invocation — parses the
`.lean` file at the surface level. Mirrors the rocq2pycsl Lark backend
in shape, with these Lean-specific additions:

  - `normalize_unicode`: rewrite ∀/∃/∧/∨/¬/→/↔/∣/≠/≤/≥ to ASCII so the
    grammar stays small.
  - Three binder shapes recognized in declarations: `(x : T)` explicit,
    `{x : T}` implicit, `[I : C T]` instance-implicit. Only the first
    survives to the AST as `BinderShape.EXPLICIT`; the others are
    recorded with their shape so the translator can strip them.
  - `@[pycsl_spec "qualname"]` attribute scanner — extracts the target
    Python qualname from the attribute literal on each theorem.
  - `termination_by ident? => <expr>` extraction.
  - `partial def` and `noncomputable def` flagged.
"""

from __future__ import annotations

import re
from pathlib import Path

from lark import Lark, Token, Transformer, UnexpectedInput, v_args

from .lean_ast import (
    Binder,
    BinderShape,
    LApp,
    LBinOp,
    LDvd,
    LeanDef,
    LeanModule,
    LeanNode,
    LExists,
    LForall,
    LLit,
    LTheorem,
    LUnaryOp,
    LUnsupported,
    LVar,
)
from .lex import Declaration, split_decls, strip_comments


# ──────────────────────────────────────────────────────────────────────
# Unicode → ASCII normalization
# ──────────────────────────────────────────────────────────────────────


# Order matters: longer keywords / multi-char glyphs first so prefix
# matches don't shadow them. We apply this rewrite to *expression text*,
# not to identifier-bearing positions, so we're conservative: each
# Unicode operator is replaced with a space-wrapped ASCII surrogate.
_UNICODE_OPS: list[tuple[str, str]] = [
    ("↔",   " <-> "),
    ("→",   " -> "),
    ("∀",   " forall "),
    ("∃",   " exists "),
    ("∧",   " /\\ "),
    ("∨",   " \\/ "),
    ("¬",   " ~ "),
    ("≠",   " <> "),
    ("≤",   " <= "),
    ("≥",   " >= "),
    ("∣",   " | "),    # divides
    ("×",   " * "),    # product type
]


def normalize_unicode(s: str) -> str:
    for u, ascii_ in _UNICODE_OPS:
        s = s.replace(u, ascii_)
    return s


# Lean method syntax mapping: when a method name follows a compound
# expression (e.g. `(divmod_pair a b).fst`), rewrite to the canonical
# function form so the translator's `_lower_app` arms catch it.
_METHOD_TO_FUNCTION: dict[str, str] = {
    "fst":    "Prod.fst",
    "snd":    "Prod.snd",
    "length": "List.length",
    "size":   "Array.size",
    "append": "List.append",
}


# ──────────────────────────────────────────────────────────────────────
# Lark setup
# ──────────────────────────────────────────────────────────────────────


_GRAMMAR_PATH = Path(__file__).with_name("lean_grammar.lark")
_PARSER = Lark.open(_GRAMMAR_PATH, parser="lalr", maybe_placeholders=False)


# ──────────────────────────────────────────────────────────────────────
# Top-level vernac dispatcher
# ──────────────────────────────────────────────────────────────────────


_ID = r"[A-Za-z_][A-Za-z_0-9']*"

# An optional attribute prefix, then the keyword, then the name + body.
_THEOREM_HEAD = re.compile(
    r"^(?:@\[(?P<attrs>[^\]]*)\]\s*)*"
    r"(?:theorem|lemma|proposition|example)\s+"
    rf"(?P<name>{_ID})\s*"
    r"(?P<rest>.*)$",
    re.DOTALL,
)

# Definitions and friends. `partial`/`noncomputable` modifiers precede `def`.
_DEF_HEAD = re.compile(
    r"^(?:@\[(?P<attrs>[^\]]*)\]\s*)*"
    r"(?P<modifiers>(?:partial|noncomputable|abbrev)\s+)*"
    r"(?:def|abbrev)\s+"
    rf"(?P<name>{_ID})\s*"
    r"(?P<rest>.*)$",
    re.DOTALL,
)

# `@[pycsl_spec "qualname"]` — extract the qualname literal.
_PYCSL_SPEC_RE = re.compile(r'pycsl_spec\s+"([^"]+)"')


def parse_module(text: str, *, source_path: str = "") -> LeanModule:
    """Top-level entry point. Returns the populated LeanModule."""
    text = strip_comments(text)
    decls = split_decls(text)

    theorems: list[LTheorem] = []
    defs: list[LeanDef] = []

    for d in decls:
        thm = _maybe_theorem(d)
        if thm is not None:
            theorems.append(thm)
            continue
        df = _maybe_def(d)
        if df is not None:
            defs.append(df)
            continue
        # Anything else (e.g. `example`, `abbrev` we didn't handle) is
        # silently ignored.

    return LeanModule(
        theorems=tuple(theorems),
        defs=tuple(defs),
        source_path=source_path,
    )


# ──────────────────────────────────────────────────────────────────────
# Theorem / definition heads
# ──────────────────────────────────────────────────────────────────────


def _maybe_theorem(d: Declaration) -> LTheorem | None:
    m = _THEOREM_HEAD.match(d.body)
    if not m:
        return None
    name = m.group("name")
    attrs = m.group("attrs") or ""
    rest = m.group("rest").strip()

    spec_target = _extract_pycsl_spec_target(attrs)

    # Drop the proof body (`:= sorry` / `:= by ...`). What remains is
    # `<binders>? : <statement-type>`.
    sig_with_type = _strip_proof_body(rest)

    # The first top-level `:` (not `:=`) separates the binders from
    # the statement type. Stop at the divides token's `|` too — but
    # divides only appears inside the *type*, so we won't see it before
    # the colon.
    colon = _find_top_level_colon(sig_with_type)
    if colon is None:
        binder_part = ""
        statement_text = sig_with_type
    else:
        binder_part = sig_with_type[:colon].strip()
        statement_text = sig_with_type[colon + 1 :].strip()

    decl_binders = _parse_decl_binders(binder_part)
    statement = _parse_statement(statement_text, d.line)

    # The statement may itself begin with `forall ...,`. Peel those
    # outer foralls into the binder list to mirror Coq's treatment
    # and keep downstream binder absorption uniform.
    extra_binders, statement = _peel_outer_forall(statement)
    binders = decl_binders + extra_binders

    return LTheorem(
        name=name,
        binders=tuple(binders),
        statement=statement,
        pycsl_spec_target=spec_target,
        source_line=d.line,
    )


def _maybe_def(d: Declaration) -> LeanDef | None:
    m = _DEF_HEAD.match(d.body)
    if not m:
        return None
    name = m.group("name")
    modifiers = (m.group("modifiers") or "").split()
    is_partial = "partial" in modifiers

    sig_with_type = _strip_proof_body(m.group("rest"))
    binders = _parse_decl_binders(sig_with_type)
    return_ty = _extract_return_type(sig_with_type)
    measure = _extract_termination_by(d.body, d.line)

    return LeanDef(
        name=name,
        params=tuple(binders),
        return_ty=return_ty,
        is_partial=is_partial,
        measure=measure,
        source_line=d.line,
    )


def _strip_proof_body(rest: str) -> str:
    """Drop everything from the first top-level `:=` to the end.

    For theorems, that's the proof term/tactics. For defs, the
    definition body. In both cases we only care about the type, so
    this lets later passes treat the prefix uniformly.
    """
    eq_at = _find_top_level_assign(rest)
    if eq_at is None:
        return rest.strip()
    return rest[:eq_at].strip()


def _extract_pycsl_spec_target(attrs: str) -> str | None:
    if not attrs:
        return None
    m = _PYCSL_SPEC_RE.search(attrs)
    return m.group(1) if m else None


# ──────────────────────────────────────────────────────────────────────
# Signature / binder splitting
# ──────────────────────────────────────────────────────────────────────


def _find_top_level_assign(s: str) -> int | None:
    """Index of the first `:=` at paren/brace-depth 0, or None."""
    depth = 0
    for i in range(len(s) - 1):
        ch = s[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0 and s[i + 1] == "=":
            return i
    return None


def _find_top_level_colon(s: str) -> int | None:
    """Index of the first `:` at paren/brace-depth 0 that is NOT `:=`."""
    depth = 0
    for i, ch in enumerate(s):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == ":" and depth == 0:
            # Skip `:=` — that's an assignment, not a type ascription.
            if i + 1 < len(s) and s[i + 1] == "=":
                continue
            return i
    return None


# Recognize `(x : T)`, `{x : T}`, `[I : C T]`. The outer delimiter
# decides the binder shape.
_GROUP_BINDER_RE = re.compile(
    r"(?P<delim>[({\[])\s*"
    rf"(?P<names>(?:{_ID}\s*)+):\s*(?P<ty>[^)}}\]]+?)\s*"
    r"[)}\]]"
)


_DELIM_SHAPE = {
    "(": BinderShape.EXPLICIT,
    "{": BinderShape.IMPLICIT,
    "[": BinderShape.INSTANCE_IMPLICIT,
}


def _parse_decl_binders(sig: str) -> list[Binder]:
    """Pull `(x y : T)`, `{x : T}`, `[I : C T]` triples out of `sig`.

    Returns the binders in source order. The translator will decide
    which to strip (instance-implicit always; implicit usually).

    Anything that doesn't match a group binder is skipped — Lean's
    bare identifier binders (`def f n m := ...` without types) aren't
    in the v1 supported subset.
    """
    out: list[Binder] = []
    for m in _GROUP_BINDER_RE.finditer(sig):
        shape = _DELIM_SHAPE[m.group("delim")]
        names = m.group("names").split()
        ty = m.group("ty").strip()
        for n in names:
            out.append(Binder(name=n, ty=ty, shape=shape))
    return out


def _extract_return_type(sig: str) -> str:
    """Take the substring after the *last* top-level `:` as the return
    type. If no top-level `:` exists outside binders, return `"_"`.
    """
    # Strip out parenthesized binder groups first so the surviving `:`
    # is the return-type ascription.
    cleaned = _GROUP_BINDER_RE.sub("", sig).strip()
    colon = _find_top_level_colon(cleaned)
    if colon is None:
        return "_"
    return cleaned[colon + 1 :].strip()


# ──────────────────────────────────────────────────────────────────────
# Termination clauses
# ──────────────────────────────────────────────────────────────────────


_TERMINATION_RE = re.compile(
    r"\btermination_by\s+(?:[A-Za-z_][A-Za-z_0-9']*\s+)*=>\s*(.*?)(?=\n\s*\S|\Z)",
    re.DOTALL,
)


def _extract_termination_by(body: str, line: int) -> LeanNode | None:
    """`termination_by ident? ... => <expr>` → parsed expression."""
    m = _TERMINATION_RE.search(body)
    if not m:
        return None
    text = m.group(1).strip()
    try:
        return _parse_statement(text, line)
    except ValueError as e:
        return LUnsupported(reason=f"termination_by parse: {e}", raw=text)


# ──────────────────────────────────────────────────────────────────────
# Statement parsing
# ──────────────────────────────────────────────────────────────────────


def _parse_statement(stmt_text: str, line: int) -> LeanNode:
    """Parse a Lean *expression* (the statement of a theorem, or the
    return-type / measure of a def). Handles Unicode normalization."""
    text = normalize_unicode(stmt_text).strip()
    if not text:
        raise ValueError(f"empty statement at line {line}")
    try:
        tree = _PARSER.parse(text)
    except UnexpectedInput as e:
        raise ValueError(
            f"failed to parse Lean expression at line {line}: {e}\n"
            f"  source: {text!r}"
        ) from e
    return _AstBuilder().transform(tree)


def _peel_outer_forall(node: LeanNode) -> tuple[list[Binder], LeanNode]:
    """If `node` is `∀ var: ty, …` (after Unicode normalization), peel
    those binders into a list and return the body.

    Each peeled binder is recorded as EXPLICIT (the parser's binders
    rule only produces those — instance/implicit don't make sense in a
    pure statement body anyway).
    """
    binders: list[Binder] = []
    cur = node
    while isinstance(cur, LForall):
        binders.append(Binder(name=cur.var, ty=cur.ty, shape=BinderShape.EXPLICIT))
        cur = cur.body
    return binders, cur


# ──────────────────────────────────────────────────────────────────────
# Lark → Lean AST
# ──────────────────────────────────────────────────────────────────────


@v_args(inline=True)
class _AstBuilder(Transformer):
    # ── atoms ──────────────────────────────────────────────────────────

    def number(self, tok: Token) -> LLit:
        return LLit(int(tok))

    def var(self, qident: str) -> LVar | LLit:
        # Lean's `True`/`False` arrive as identifiers; promotion to
        # boolean Lit happens in the translator.
        return LVar(qident)

    def qident(self, *parts: Token) -> str:
        return ".".join(str(p) for p in parts)

    def type_expr(self, ty: str) -> str:
        return ty

    def ty_arrow(self, *parts: str) -> str:
        return " -> ".join(p for p in parts)

    def ty_prod(self, *parts) -> str:
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

    # ── binders inside expressions ─────────────────────────────────────

    def typed_group_binder(self, *items) -> list[tuple[str, str]]:
        *names, ty = items
        return [(str(n), ty) for n in names]

    def bare_binder(self, *names: Token) -> list[tuple[str, str]]:
        return [(str(n), "_") for n in names]

    def binders(self, *groups) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for g in groups:
            out.extend(g)
        return out

    # ── application ────────────────────────────────────────────────────

    def app_chain(self, head: LeanNode, *args: LeanNode) -> LeanNode:
        if not args:
            return head
        if isinstance(head, LVar):
            return LApp(fn=head.name, args=tuple(args))
        return LUnsupported(
            reason="higher-order application",
            raw=str(head),
        )

    # ── method syntax: `(expr).fst` / `l.length` ─────────────────────

    def dot_field(self, name: Token) -> str:
        """Lark callback for a `.IDENT` suffix — return just the field name."""
        return str(name)

    def postfix_atom(self, base: LeanNode, *fields: str) -> LeanNode:
        """Apply chained `.field` suffixes to a base atom.

        - `t.fst`  on `LVar("t")` → `LVar("t.fst")` (qident-style; the
          translator's dot-syntax recognizer handles it downstream).
        - `(expr).fst` on a compound base → `LApp("Prod.fst", (base,))`
          so the translator's `_lower_app` path catches it.
        """
        cur = base
        for field in fields:
            if isinstance(cur, LVar):
                # Append to the qident so the dot-syntax path in the
                # translator recognizes it as a single dotted name.
                cur = LVar(name=f"{cur.name}.{field}")
            else:
                # Compound base — map field name to the canonical Lean
                # `Prod.fst` / `Prod.snd` / etc. and apply as a function.
                fn_name = _METHOD_TO_FUNCTION.get(field, f"_field.{field}")
                cur = LApp(fn=fn_name, args=(cur,))
        return cur

    # ── arithmetic chains ─────────────────────────────────────────────

    def add_chain(self, first: LeanNode, *rest) -> LeanNode:
        return _left_assoc_chain(first, rest)

    def mul_chain(self, first: LeanNode, *rest) -> LeanNode:
        return _left_assoc_chain(first, rest)

    def neg(self, operand: LeanNode) -> LUnaryOp:
        return LUnaryOp(op="-", arg=operand)

    # ── comparisons / divides ──────────────────────────────────────────

    def cmp(self, lhs: LeanNode, *rest) -> LeanNode:
        if not rest:
            return lhs
        op_tok, rhs = rest
        return LBinOp(op=str(op_tok), lhs=lhs, rhs=rhs)

    def dvd(self, a: LeanNode, b: LeanNode) -> LDvd:
        return LDvd(a=a, b=b)

    # ── logical ────────────────────────────────────────────────────────

    def negation(self, operand: LeanNode) -> LUnaryOp:
        return LUnaryOp(op="~", arg=operand)

    def andexp(self, lhs: LeanNode, *rest) -> LeanNode:
        # rest is either () or (AND_OP_token, rhs).
        if not rest:
            return lhs
        # Strip any literal-operator token (priority-3 named terminals
        # appear here when the grammar rule references them by name).
        operands = [x for x in rest if not isinstance(x, Token)]
        if not operands:
            return lhs
        (rhs,) = operands
        return LBinOp(op="/\\", lhs=lhs, rhs=rhs)

    def orexp(self, lhs: LeanNode, *rest) -> LeanNode:
        if not rest:
            return lhs
        operands = [x for x in rest if not isinstance(x, Token)]
        if not operands:
            return lhs
        (rhs,) = operands
        return LBinOp(op="\\/", lhs=lhs, rhs=rhs)

    def impl(self, lhs: LeanNode, *rest) -> LeanNode:
        if not rest:
            return lhs
        (rhs,) = rest
        return LBinOp(op="->", lhs=lhs, rhs=rhs)

    def iff(self, lhs: LeanNode, *rest) -> LeanNode:
        if not rest:
            return lhs
        (rhs,) = rest
        return LBinOp(op="<->", lhs=lhs, rhs=rhs)

    # ── quantifiers ────────────────────────────────────────────────────

    def forall_expr(self, binders: list[tuple[str, str]], body: LeanNode) -> LeanNode:
        node = body
        for var, ty in reversed(binders):
            node = LForall(var=var, ty=ty, body=node)
        return node

    def exists_expr(self, binders: list[tuple[str, str]], body: LeanNode) -> LeanNode:
        node = body
        for var, ty in reversed(binders):
            node = LExists(var=var, ty=ty, body=node)
        return node

    def start(self, expr: LeanNode) -> LeanNode:
        return expr


def _left_assoc_chain(first: LeanNode, rest: tuple) -> LeanNode:
    cur = first
    it = iter(rest)
    for op_tok in it:
        rhs = next(it)
        cur = LBinOp(op=str(op_tok), lhs=cur, rhs=rhs)
    return cur
