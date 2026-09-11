"""PyCSL exception trigger model — central source of truth for the
mapping from IR operations to the implicit Python exceptions they may
raise and the WhyML trigger conditions that prevent them.

See `config/skills/pycsl-exception-model/SKILL.md` for the human-facing
specification. The table below mirrors §3 of
`NoException_and_UBDetection_Workplan.md` (Phase 1).

This module is imported by Module 4 (semantic validation of
`no_exception` clauses) and Module 6 (`module6_whyml/expressions.py`,
`statements.py`, `preamble.py` — VC injection and predicate library).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


# ----------------------------------------------------------------------
# 1. Authoritative exception set
# ----------------------------------------------------------------------
# Phase 1 — exceptions with clean mathematical triggers. New entries here
# must also gain a row in TRIGGERS below and a corpus test under
# test-suite/corpus/pycsl-reference/.

KNOWN_EXCEPTIONS: frozenset = frozenset({
    "ZeroDivisionError",
    "IndexError",
    "KeyError",
    "ValueError",
    "StopIteration",
})


# ----------------------------------------------------------------------
# 1b. Exception subclass hierarchy
# ----------------------------------------------------------------------
# PyCSL otherwise treats exception names as flat, distinct tokens. The os
# model (and faithful Python in general) relies on `except OSError:`
# catching a raised subclass such as `FileNotFoundError`, and on
# `#@ raises OSError` summarising the subclass raises.
#
# `EXCEPTION_BASES[E]` is the tuple of E's *direct* base class names, in
# Python MRO order (most-derived base first). The reflexive-transitive
# closure (`bases_closure`) gives the full set of ancestors of E; a
# handler `except B` catches a raised `E` iff `E == B` or `B in
# bases_closure(E)`.
#
# `OSError` is deliberately kept OUT of KNOWN_EXCEPTIONS: it has no
# mathematical implicit trigger. It (and its subclasses) is raised on an
# explicit failure CONDITION in the body (e.g. `if lookup(p) < 0: raise
# FileNotFoundError`), exactly like the `SyntaxError` precedent. The
# hierarchy below only governs handler matching and `raises`
# summarisation — it does not auto-inject any VC.

EXCEPTION_BASES: Dict[str, Tuple[str, ...]] = {
    # --- the OSError family (the os-module faithfulness fix) ---------
    "OSError":            ("Exception",),
    "FileNotFoundError":  ("OSError", "Exception"),
    "FileExistsError":    ("OSError", "Exception"),
    "PermissionError":    ("OSError", "Exception"),
    "NotADirectoryError": ("OSError", "Exception"),
    "IsADirectoryError":  ("OSError", "Exception"),
    "InterruptedError":   ("OSError", "Exception"),
    "BlockingIOError":    ("OSError", "Exception"),
    "ChildProcessError":  ("OSError", "Exception"),
    "ConnectionError":    ("OSError", "Exception"),
    "ProcessLookupError": ("OSError", "Exception"),
    "TimeoutError":       ("OSError", "Exception"),
    # `os.error` is documented as an alias for OSError (os.rst l.51-53).
    # Treat it as a synonym so `except os.error` behaves like
    # `except OSError`.
    "error":              ("OSError", "Exception"),
}


def bases_closure(exc: str) -> frozenset:
    """Return the reflexive-transitive set of ancestor class names of
    `exc` (NOT including `exc` itself). Unknown names — exceptions not in
    EXCEPTION_BASES — have no modelled ancestors (the flat-token default),
    so this returns an empty set, preserving the legacy behaviour for
    every exception outside the hierarchy."""
    seen: set = set()
    frontier = list(EXCEPTION_BASES.get(exc, ()))
    while frontier:
        b = frontier.pop()
        if b in seen:
            continue
        seen.add(b)
        frontier.extend(EXCEPTION_BASES.get(b, ()))
    return frozenset(seen)


def handler_catches(handler_exc: str, raised_exc: str) -> bool:
    """True iff a `except handler_exc:` clause catches a raised
    `raised_exc` — i.e. they are the same name, or `handler_exc` is an
    ancestor of `raised_exc` in the modelled hierarchy. Names outside the
    hierarchy match only themselves (legacy flat-token semantics)."""
    if handler_exc == raised_exc:
        return True
    return handler_exc in bases_closure(raised_exc)


def subclasses_of(base: str, candidates) -> frozenset:
    """Return the members of `candidates` that are caught by a
    `except base:` handler (base itself, or any strict subclass of base
    present in `candidates`). Used to expand a handler into the concrete
    raised tags it must match in WhyML, and to compute which raised
    exceptions a handler actually catches for the escaping-set analysis."""
    return frozenset(c for c in candidates if handler_catches(base, c))


# ----------------------------------------------------------------------
# 2. WhyML predicate library
# ----------------------------------------------------------------------
# Each predicate is emitted into the WhyML preamble when at least one
# function in the file uses no_exception. The body is plain WhyML syntax.
# Keep these definitions stable — changing a predicate body changes every
# proof obligation that references it.

PREDICATE_LIBRARY: Dict[str, str] = {
    "no_div_zero":   "predicate no_div_zero (b: int) = b <> 0",
    "in_bounds":     "predicate in_bounds (n: int) (i: int) = 0 <= i /\\ i < n",
    "non_neg_shift": "predicate non_neg_shift (n: int) = n >= 0",
}


# ----------------------------------------------------------------------
# 3. Trigger table
# ----------------------------------------------------------------------
# Each entry maps an IR operation key to a list of triggers. A trigger is
# (exception_name, trigger_expr_template) where trigger_expr_template is
# a WhyML expression with positional placeholders {0}, {1}, ... that are
# substituted with the operands' WhyML strings at emission time.
#
# Key shape:
#   ("binop", op_name)              — IR BinOp with op == op_name
#   ("subscript", "read"|"write")   — array indexing
#   ("call", "name")                — function call by simple name
#   ("attr_call", "method")         — method call (any receiver)
#   ("map_get", None)               — dict subscript / \map_get
#
# Substitution semantics (positional):
#   binop "/":     {0} = left, {1} = right       → no_div_zero ({1})
#   subscript:     {0} = array_len_expr, {1} = i → in_bounds ({0}) ({1})
#   map_get:       {0} = dict_expr, {1} = key    → has_key ({0}) ({1})
#                  (has_key is provided by the existing ghost-dict
#                  predicate vocabulary; no preamble emission needed.)

Trigger = Tuple[str, str]   # (exception_name, whyml_predicate_template)

TRIGGERS: Dict[Tuple[str, Optional[str]], List[Trigger]] = {
    # Arithmetic — keys match the IR's BinOp `op` field. Module 5 emits
    # Python `/`, `//`, `%` after normalization (via `op_translate`) as
    # `div` and `mod`, so the table keys mirror what the binop handler
    # actually sees.
    ("binop", "div"): [("ZeroDivisionError", "no_div_zero ({1})")],
    ("binop", "mod"): [("ZeroDivisionError", "no_div_zero ({1})")],
    ("binop", "/"):   [("ZeroDivisionError", "no_div_zero ({1})")],
    ("binop", "//"):  [("ZeroDivisionError", "no_div_zero ({1})")],
    ("binop", "%"):   [("ZeroDivisionError", "no_div_zero ({1})")],
    ("binop", "<<"):  [("ValueError",        "non_neg_shift ({1})")],
    ("binop", ">>"):  [("ValueError",        "non_neg_shift ({1})")],

    # Indexing — {0} is the array-length expression supplied at the call
    # site, {1} is the index. The Module 6 emitter looks up the array's
    # length via the same machinery that supports `\length(arr)`.
    ("subscript", "read"):  [("IndexError", "in_bounds ({0}) ({1})")],
    ("subscript", "write"): [("IndexError", "in_bounds ({0}) ({1})")],
    # (#49) ROUTE #64 — AN ELEMENT STORE TO A `bytes`/`bytearray` RECEIVER also raises
    # `ValueError` when the value is out of [0, 256). There was no entry for this at all,
    # so `#@ no_exception \all` — which expands to the whole KNOWN_EXCEPTIONS set, and
    # `ValueError` IS in it — PROVED for `b = bytearray([1]); b[0] = 999; return b[0]`,
    # which raises `ValueError: byte must be in range(0, 256)` in CPython. Measured that
    # the machinery itself works: `a // 0` under `no_exception ZeroDivisionError` does NOT
    # prove and `a // b` with `requires b != 0` DOES, so this was a missing ROW, not a
    # broken mechanism.
    #
    # A SEPARATE KEY, not a second trigger on ("subscript", "write"): that key is shared
    # with plain lists, whose elements are ordinary ints and must NOT acquire a byte-range
    # obligation. The emitter selects this key only when the receiver's type is known to be
    # `bytes`/`bytearray`. {0} is the stored VALUE.
    # INLINE, like the `map_get` row above and deliberately NOT a new entry in
    # PREDICATE_LIBRARY: that library is emitted WHOLESALE into the preamble of every unit
    # declaring `no_exception`, so adding a predicate there moved 31 corpus emissions by one
    # inert definition line — measured. An inline condition keeps the repair byte-inert on
    # every program that does not actually store into a bytes receiver.
    ("subscript", "write_bytes"): [("ValueError", "0 <= {0} /\\ {0} < 256")],
    # (#49) ROUTE #66 — `del d[k]` on a LOCAL dict raises `KeyError` when the key is absent.
    # The operation lowers FAITHFULLY (`d := map_update_none !d k`) and carried no obligation
    # at all, so `#@ no_exception KeyError` PROVED for `d = {1:1}; del d[5]`. Same condition
    # the `("attr_call", "pop")` row already carries. WIRED rather than refused, because
    # unlike `divmod`/`int(str)` the receiver here is a real modelled map, so the obligation
    # is faithful and a correct program still discharges it.
    ("subscript", "del"): [("KeyError", "Map.get {0} {1} <> None")],
    # (#49) ROUTE #66 — `chr(n)` raises `ValueError` outside [0, 0x110000). The abstract
    # `chr_op` carried `ensures { String.length result = 1 }` UNCONDITIONALLY, i.e. it
    # asserted a TOTALITY Python does not have, and there was no trigger row, so
    # `#@ no_exception \all` PROVED for `chr(-1)`. WIRED rather than refused: the bound is
    # exact, so `chr(65)` still discharges.
    ("call", "chr"): [("ValueError", "0 <= {0} /\\ {0} < 1114112")],
    # (#49) ROUTE #67 — a STRING subscript read raises `IndexError` out of range, and went
    # down the `char_code_at` path that no row covered while the ARRAY read (below) was
    # wired all along. `{0}` is the string, `{1}` the index. `in_bounds` is already in
    # PREDICATE_LIBRARY, and an `assert` is a LOGIC context, so `String.length` is legal
    # here even though it is not in a program term.
    ("subscript", "read_str"): [("IndexError", "in_bounds (String.length {0}) ({1})")],

    # Dict access — inline `Map.get d k <> None` rather than a separate
    # predicate, mirroring the existing ghost-dict vocabulary so we don't
    # have to add `has_key` to the WhyML preamble.
    ("map_get", None): [("KeyError", "Map.get {0} {1} <> None")],

    # Builtin and dotted calls.
    ("call", "divmod"):       [("ZeroDivisionError", "no_div_zero ({1})")],
    ("attr_call", "pop"):     [("KeyError",          "Map.get {0} {1} <> None")],
    ("attr_call", "index"):   [("ValueError",        "true")],  # placeholder; \mem when proof needs it
    ("call", "next"):         [("StopIteration",     "true")],  # Phase 2 — left as a marker
}


def triggers_for(op_key: Tuple[str, Optional[str]]) -> List[Trigger]:
    """Return the list of (exception, trigger_template) pairs for an IR
    operation key. Empty list means the operation cannot raise a Phase 1
    implicit exception."""
    return TRIGGERS.get(op_key, [])


def predicate_definitions(needed: Optional[set] = None) -> List[str]:
    """Return WhyML lines defining the predicates the caller needs.
    Pass ``needed`` as a set of predicate names to emit only those, or
    None to emit the whole library."""
    if needed is None:
        return list(PREDICATE_LIBRARY.values())
    return [v for k, v in PREDICATE_LIBRARY.items() if k in needed]


def all_phase1_exceptions() -> List[str]:
    """Expansion target for `no_exception \\all`. Returns a sorted list
    so emission order is deterministic across runs."""
    return sorted(KNOWN_EXCEPTIONS)
