from __future__ import annotations

import unicodedata
from typing import Dict, Set


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


def op_translate(op: str) -> str:
    """Translates operators; defaults to the same string (e.g., +, -, >, <)."""
    return OP_MAP.get(op, op)
