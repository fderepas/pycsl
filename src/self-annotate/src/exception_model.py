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


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def triggers_for(op_key: Tuple[str, Optional[str]]) -> List[Trigger]:
    """Return the list of (exception, trigger_template) pairs for an IR
    operation key. Empty list means the operation cannot raise a Phase 1
    implicit exception.

    Annotation rationale: lookup in a tuple-keyed dict; PyCSL cannot
    model tuple-key dict access today. Reviewer attests the interface
    (returns a list; never raises; pure)."""
    return TRIGGERS.get(op_key, [])


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def predicate_definitions(needed: int = 0) -> List[str]:  # mirror: opaque-int placeholder for Optional[set]
    """Return WhyML lines defining the predicates the caller needs.
    Pass ``needed`` as a set of predicate names to emit only those, or
    None to emit the whole library.

    Annotation rationale: list comprehension + dict iteration; PyCSL
    cannot model these yet."""
    if needed is None:
        return list(PREDICATE_LIBRARY.values())
    return [v for k, v in PREDICATE_LIBRARY.items() if k in needed]


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def all_phase1_exceptions() -> List[str]:
    """Expansion target for `no_exception \\all`. Returns a sorted list
    so emission order is deterministic across runs.

    Annotation rationale: `sorted()` on a frozenset; PyCSL cannot model
    `frozenset` iteration."""
    return sorted(KNOWN_EXCEPTIONS)
