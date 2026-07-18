from __future__ import annotations

import hashlib
import unicodedata
from typing import Dict, List, Set


def stable_hash(s: str) -> int:
    """Deterministic, process-independent hash of a string to a non-negative int
    in [0, 2147483647). Replaces Python's built-in `hash()` for the legacy
    opaque-string→int fallback: `hash()` randomizes `str` hashing per process
    (PYTHONHASHSEED), which made WhyML emission non-reproducible (different
    `decode`/`str_hash` constants run-to-run). This gives the same value on every
    run and machine — required for the byte-diff reproducibility gate — while
    preserving the distinguishing property (distinct strings → distinct ints w.h.p.)."""
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % 2147483647


# Maps Python/IR operators to WhyML operators
OP_MAP: Dict[str, str] = {
    "==": "=",    # WhyML equality is single =
    "!=": "<>",   # WhyML inequality is <>
    "==>": "->",  # WhyML implication
    "<==>": "<->",  # WhyML equivalence
    "and": "&&",
    "or": "||",
    "not": "not",
    "div": "div",
    "//": "div",  # contract floor-division maps to WhyML div
    "/": "div",   # contract `/` maps to WhyML `div` (Euclidean integer division)
    "%": "mod",   # WhyML modulo from int.EuclideanDivision
}


# WhyML reserved keywords that cannot be used as identifiers
WHYML_RESERVED: Set[str] = {
    "at", "any", "diverges", "val", "let", "in", "if", "then", "else",
    "while", "do", "done", "for", "to", "begin", "end", "match", "with",
    "try", "raise", "exception", "type", "use", "module", "theory",
    "import", "export", "clone", "goal", "lemma", "axiom", "predicate",
    "function", "constant", "mutable", "ghost", "invariant", "variant",
    "requires", "ensures", "returns", "raises", "reads", "writes",
    "assert", "assume", "check", "absurd", "true", "false", "not",
    "old", "ref", "abstract", "private", "model", "range",
    "float", "by", "so", "pure", "alias", "label", "epsilon",
    "exists", "forall", "rec", "and", "or", "mod", "div", "result",
    # `partial` marks a possibly-diverging function in Why3 (`let partial f …`),
    # so a Python function/var named `partial` (e.g. functools.partial) must be
    # mangled or `let partial (…)` is a syntax error.
    "partial", "fun", "as", "scope", "coinductive", "inductive",
    # `return` is a WhyML keyword. No Python IDENTIFIER can ever be literally
    # `return` (it is a Python keyword too), so this is corpus-inert — it only
    # bites the stmt-list-append-mutation wall's `ast.Return` record, whose type
    # name lowercases to `return` and must mangle to `py_return` (the `assert` ->
    # `py_assert` precedent) or `type return = …` is a syntax error.
    "return",
}


def whyml_ident(name: str) -> str:
    """WhyML identifiers must start with a lowercase letter, contain no dots,
    and not be reserved keywords."""
    # Underscore alone is a wildcard in WhyML — rename it
    if name == "_":
        return "py_underscore"
    # Replace dots with underscores for valid WhyML identifiers
    name = name.replace(".", "_")
    # Sanitize non-ASCII characters to ASCII equivalents
    sanitized = []
    for ch in name:
        if ord(ch) > 127:
            decomp = unicodedata.normalize('NFD', ch)
            ascii_ch = ''.join(c for c in decomp if ord(c) < 128)
            sanitized.append(ascii_ch if ascii_ch else f"u{ord(ch)}")
        else:
            sanitized.append(ch)
    name = ''.join(sanitized)
    if name and name[0].isupper():
        name = name[0].lower() + name[1:]
    # Prefix reserved words to avoid conflicts
    if name in WHYML_RESERVED:
        name = f"py_{name}"
    return name


def safe_mutex_name(mutex: str) -> str:
    """Convert a mutex expression (possibly 'locks[0]') to a valid WhyML identifier."""
    return whyml_ident(mutex.replace("[", "_").replace("]", "").replace(".", "_"))


def safe_exc_name(name: str) -> str:
    """Sanitize a user-exception name for WhyML emission.

    Python local-alias imports (`from X import Y as _Y`) produce
    exception names starting with `_`, which WhyML rejects in
    exception-declaration position. Stripping leading underscore(s)
    yields a valid WhyML identifier; the de-aliased name also
    collapses with the original (un-prefixed) declaration via set
    deduplication at the call site, so `Y` and `_Y` emit a single
    `exception Y` declaration."""
    return name.lstrip("_") or name


def op_translate(op: str) -> str:
    """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
    return OP_MAP.get(op, op)


# Why3 string-literal escape map (see why3 `src/util/lexlib.mll`: rule `string`).
# Why3 accepts printable ASCII (codepoints 32..126) verbatim inside a `"..."` and
# supports the backslash escapes below. Any other raw byte — notably a raw newline
# (LF, CR), tab, or non-ASCII/control character — raises "illegal character in
# string", which previously made Python `"\n"` lower to a WhyML literal that Why3
# rejected. `\xHH` (two hex digits) is the catch-all for the remaining range.
_WHYML_STR_ESCAPES = {
    '\\': '\\\\',
    '"':  '\\"',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
    '\b': '\\b',
}


def whyml_string_literal(value: str) -> str:
    """Render a Python `str` as a WhyML string literal.

    Why3 string literals (`"..."`) accept printable ASCII (codepoints 32..126)
    verbatim plus the backslash escapes `\\\\` `\\"` `\\n` `\\r` `\\t` `\\b`
    (see `src/util/lexlib.mll`, rule `string`). Every other codepoint — raw
    newlines, tabs, control bytes, non-ASCII — must be encoded as `\\xHH` or
    Why3 rejects the literal with "illegal character in string". This used to
    block any body-faithful annotation of code that builds strings containing
    `";\\n"` (e.g. the `_handle_*` WhyML emitters). All escapes here are
    accepted by Why3's lexer, so the emitted literal needs no `use string.Char`
    and stays byte-identical for the common case (printable ASCII, no
    backslash/quote) — only strings that previously failed to parse change.
    """
    out: List[str] = []
    for ch in value:
        esc = _WHYML_STR_ESCAPES.get(ch)
        if esc is not None:
            out.append(esc)
        elif 32 <= ord(ch) <= 126:
            out.append(ch)
        else:
            # Encode the codepoint's UTF-8 bytes as `\xHH` pairs. Why3's
            # `string.Char` models Latin-1 (0..255); for codepoints > 255
            # (e.g. emoji) this preserves the byte sequence Why3 would itself
            # produce for an equivalent literal entered in a UTF-8 source.
            for b in ch.encode("utf-8"):
                out.append(f"\\x{b:02x}")
    return '"' + ''.join(out) + '"'
