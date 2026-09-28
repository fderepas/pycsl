from __future__ import annotations

import hashlib
import unicodedata
from typing import Dict, List, Set


# (#49) ROUTE #228 — THE "w.h.p." PREMISE IS NOW A CHECKED ONE INSTEAD OF AN ARGUMENT.
#
# `stable_hash` used to justify itself with "preserving the distinguishing property
# (distinct strings -> distinct ints **w.h.p.**)". That is a PROBABILISTIC premise,
# load-bearing in a DEDUCTIVE verifier's trusted computing base, and it was the whole
# of the justification. It is sha256 truncated to **32 bits**, so a birthday collision
# costs ~2^16 trials — UNDER ONE SECOND of compute — and the `% (2^31-1)` fold makes
# `h` and `h + 0x7FFFFFFF` collide DETERMINISTICALLY. Measured: `'f9r'` and `'6xb'`,
# two THREE-character strings, both fold to 122473869 (found after 46067 candidates).
#
# THE COLLAPSE ONLY *CONCLUDES* A FALSEHOOD WHERE THE RECEIVING Why3 SYMBOL IS PURE.
# Every bare `val` destination is non-deterministic, so two equal arguments relate
# nothing — measured VACUOUS: the witness AND its non-colliding control both failed to
# prove, which is what "measured nothing" looks like. Dict keys, list literals and set
# literals are faithful native strings and never fold. The one PURE destination is
#
#     val function struct_{pack,unpack}_<slot_id> (fmt: int) ...
#
# deliberately pure — "both program-callable and a logical symbol the round-trip axiom
# can name" — and `slot_id` encodes "only the slot types (not prefix, not pad)", so
# unbounded pad/prefix variants of one format share ONE symbol and differ ONLY in this
# folded int:
#
#     struct.pack('<bb6x', 1, 2)                  CPython:  8 bytes
#     struct.pack('<xxxxxxxxhxLxxxxxxxx', 1, 2)   CPython: 23 bytes
#     both emit  (struct_pack_i2 1322019588 1 2)     <-- ONE TERM
#
# so `len(a) == len(b)` proved Valid in 156 steps and `\result == 1` was PROVEN while
# CPython returns 0. See `getting-better/open-routes/route228-*`.
#
# THE FIX IS NOT A WIDER HASH. More bits lowers the probability and keeps the premise
# probabilistic — route #227's lesson in a new costume: an opaque answer to a wrong
# value moves the falsehood rather than removing it. The premise is INJECTIVITY OF THE
# FOLD ON THE STRINGS ONE EMISSION ACTUALLY FOLDS, and that is a DECIDABLE property of
# that emission. So record it and REFUSE — fail-closed, a measurement and not an
# argument.
#
# SCOPE. `pycsl.py` runs one emission per process (`bin/byte-diff-sweep.sh` and
# `bin/run-reference-tests.sh` both invoke it per file), so a CLI run's witness never spans
# two programs. That is NOT true of every caller, and saying "per-emission by construction"
# would be exactly the kind of argued premise this guard replaces: `bin/core-only-
# conformance.py` and `bin/regen-ir-conformance-goldens.py` construct
# `Module6_WhyMLTranspiler(...)` IN-PROCESS in a loop, so their witnesses DO accumulate
# across files. MEASURED rather than argued: `core-only-conformance.py` runs 38 goldens in
# one process and accumulates **ZERO** folds (they contain no foldable string), and it is
# green with this guard. So the largest accumulation anywhere measured is the 91 below, from
# a single mirror emission.
#
# POPULATION, MEASURED, because a guard whose population is empty has checked nothing
# and looks exactly like a guard that passed: the LARGEST emission in this tree folds
# **91** distinct strings (`src/self-annotate/src/frontend/pure_ast.py`; the mirror
# `expressions.py` folds 4, `statements.py` 7, a struct corpus file 1). At 91 strings
# the collision probability is ~2e-6, so this guard is byte-inert on everything that
# exists today and its population IS empty. It is therefore NEGATIVE-TESTED against the
# pair above by `bin/check-stable-hash-fold-injectivity.py`, which asserts PyCSL REFUSES
# the colliding program and still ACCEPTS the non-colliding control.
_FOLD_WITNESS: Dict[int, str] = {}


def stable_hash(s: str) -> int:
    """Deterministic, process-independent, and CHECKED-INJECTIVE fold of a string to a
    non-negative int in [0, 2147483647). Replaces Python's built-in `hash()` for the
    legacy opaque-string→int fallback: `hash()` randomizes `str` hashing per process
    (PYTHONHASHSEED), which made WhyML emission non-reproducible (different
    `decode`/`str_hash` constants run-to-run). This gives the same value on every run
    and machine — required for the byte-diff reproducibility gate.

    The distinguishing property (distinct strings -> distinct ints) is NO LONGER
    claimed "w.h.p." and is no longer assumed: it is VERIFIED for the strings this
    emission actually folds, and a collision REFUSES the file. See route #228 above."""
    h = int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % 2147483647
    _seen = _FOLD_WITNESS.setdefault(h, s)
    if _seen != s:
        from errors import PyCSLSemanticError
        raise PyCSLSemanticError(
            f"internal string-fold collision (route #228): {s!r} and {_seen!r} are "
            f"DISTINCT strings that both fold to the constant {h}. PyCSL encodes a "
            f"string it cannot model faithfully as this constant, and a pure Why3 "
            f"symbol applied to it (struct.pack/struct.unpack's `fmt`) would then be "
            f"THE SAME TERM for both — so the proof could establish a false claim "
            f"about them. Refused rather than emitted. How to fix: if either string "
            f"is a struct format, respell it equivalently ('6x' for 'xxxxxx', or a "
            f"different byte-order prefix spelling) — that changes the constant "
            f"without changing the format's meaning, and this same check re-verifies "
            f"the result. Otherwise please report it: a collision here is a defect in "
            f"PyCSL's encoding, not in your program.")
    return h


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
