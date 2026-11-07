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
    # (#49) ROUTE #260 — THE WHOLE BUILTIN HIERARCHY, NOT ONLY THE OSError FAMILY. Why3
    # matches `with` / `raises` arms by EXACT tag, so a builtin class missing here was a
    # flat token: `try: raise KeyError(...) except LookupError: r = 7` lowered to
    # `try raise KeyError with LookupError -> ...`, the raise escaped the handler into an
    # added `raises { KeyError }`, and `\result == 0` PROVED (CPython 7). Every CPython
    # builtin exception class now lists ALL its proper ancestors (CPython 3.14 `__mro__`
    # minus `object`), so `except LookupError` / `ArithmeticError` / `ValueError` /
    # `Exception` / `BaseException` expand to an arm for every raised subclass. Data only:
    # `bases_closure` / `handler_catches` are unchanged.
    "ArithmeticError": ("Exception", "BaseException"),
    "AssertionError": ("Exception", "BaseException"),
    "AttributeError": ("Exception", "BaseException"),
    "BaseExceptionGroup": ("BaseException",),
    "BlockingIOError": ("OSError", "Exception", "BaseException"),
    "BrokenPipeError": ("ConnectionError", "OSError", "Exception", "BaseException"),
    "BufferError": ("Exception", "BaseException"),
    "BytesWarning": ("Warning", "Exception", "BaseException"),
    "ChildProcessError": ("OSError", "Exception", "BaseException"),
    "ConnectionAbortedError": ("ConnectionError", "OSError", "Exception", "BaseException"),
    "ConnectionError": ("OSError", "Exception", "BaseException"),
    "ConnectionRefusedError": ("ConnectionError", "OSError", "Exception", "BaseException"),
    "ConnectionResetError": ("ConnectionError", "OSError", "Exception", "BaseException"),
    "DeprecationWarning": ("Warning", "Exception", "BaseException"),
    "EOFError": ("Exception", "BaseException"),
    "EncodingWarning": ("Warning", "Exception", "BaseException"),
    "Exception": ("BaseException",),
    "ExceptionGroup": ("BaseExceptionGroup", "Exception", "BaseException"),
    "FileExistsError": ("OSError", "Exception", "BaseException"),
    "FileNotFoundError": ("OSError", "Exception", "BaseException"),
    "FloatingPointError": ("ArithmeticError", "Exception", "BaseException"),
    "FutureWarning": ("Warning", "Exception", "BaseException"),
    "GeneratorExit": ("BaseException",),
    "ImportError": ("Exception", "BaseException"),
    "ImportWarning": ("Warning", "Exception", "BaseException"),
    "IndentationError": ("SyntaxError", "Exception", "BaseException"),
    "IndexError": ("LookupError", "Exception", "BaseException"),
    "InterruptedError": ("OSError", "Exception", "BaseException"),
    "IsADirectoryError": ("OSError", "Exception", "BaseException"),
    "KeyError": ("LookupError", "Exception", "BaseException"),
    "KeyboardInterrupt": ("BaseException",),
    "LookupError": ("Exception", "BaseException"),
    "MemoryError": ("Exception", "BaseException"),
    "ModuleNotFoundError": ("ImportError", "Exception", "BaseException"),
    "NameError": ("Exception", "BaseException"),
    "NotADirectoryError": ("OSError", "Exception", "BaseException"),
    "NotImplementedError": ("RuntimeError", "Exception", "BaseException"),
    "OSError": ("Exception", "BaseException"),
    "OverflowError": ("ArithmeticError", "Exception", "BaseException"),
    "PendingDeprecationWarning": ("Warning", "Exception", "BaseException"),
    "PermissionError": ("OSError", "Exception", "BaseException"),
    "ProcessLookupError": ("OSError", "Exception", "BaseException"),
    "PythonFinalizationError": ("RuntimeError", "Exception", "BaseException"),
    "RecursionError": ("RuntimeError", "Exception", "BaseException"),
    "ReferenceError": ("Exception", "BaseException"),
    "ResourceWarning": ("Warning", "Exception", "BaseException"),
    "RuntimeError": ("Exception", "BaseException"),
    "RuntimeWarning": ("Warning", "Exception", "BaseException"),
    "StopAsyncIteration": ("Exception", "BaseException"),
    "StopIteration": ("Exception", "BaseException"),
    "SyntaxError": ("Exception", "BaseException"),
    "SyntaxWarning": ("Warning", "Exception", "BaseException"),
    "SystemError": ("Exception", "BaseException"),
    "SystemExit": ("BaseException",),
    "TabError": ("IndentationError", "SyntaxError", "Exception", "BaseException"),
    "TimeoutError": ("OSError", "Exception", "BaseException"),
    "TypeError": ("Exception", "BaseException"),
    "UnboundLocalError": ("NameError", "Exception", "BaseException"),
    "UnicodeDecodeError": ("UnicodeError", "ValueError", "Exception", "BaseException"),
    "UnicodeEncodeError": ("UnicodeError", "ValueError", "Exception", "BaseException"),
    "UnicodeError": ("ValueError", "Exception", "BaseException"),
    "UnicodeTranslateError": ("UnicodeError", "ValueError", "Exception", "BaseException"),
    "UnicodeWarning": ("Warning", "Exception", "BaseException"),
    "UserWarning": ("Warning", "Exception", "BaseException"),
    "ValueError": ("Exception", "BaseException"),
    "Warning": ("Exception", "BaseException"),
    "ZeroDivisionError": ("ArithmeticError", "Exception", "BaseException"),
    # `os.error` is documented as an alias for OSError (os.rst l.51-53).
    # Treat it as a synonym so `except os.error` behaves like
    # `except OSError`.
    "error":              ("OSError", "Exception", "BaseException"),
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
    # (#49) ROUTE #68 — `0 ** -1` raises `ZeroDivisionError` in Python (a zero base cannot be
    # raised to a negative power). Both operands are available at the call site, so the
    # condition is EXACT and a correct power still discharges. NOTE the two rows above were
    # in the table all along and were NOT being injected: the `<<`/`>>` emission goes through
    # the bitwise/power path, which did not wrap, so `1 << -1` PROVED under
    # `#@ no_exception \all` while CPython raises `ValueError`. That path now wraps.
    ("binop", "**"):  [("ZeroDivisionError", "not ({0} = 0 /\\ {1} < 0)")],

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
    # (#49) ROUTE #281 — int -> DECIMAL str raises `ValueError` past 4300 digits
    # (CPython 3.11+ `sys.int_max_str_digits`, default 4300): `str(10**5000)`,
    # `f"{x}"`, `print(x)`, `repr(x)`, `"%d" % x` all raise "Exceeds the limit (4300
    # digits) for integer string conversion". 4300 digits is exactly |x| < 10**4300.
    # {0} is the int operand. Wired at every int->decimal-string conversion site the
    # emitter lowers (`str`/`repr` of an int, a non-string `print` argument, an int
    # f-string part — plain, `!s`/`!r`/`!a`, or a decimal spec —, a `%` format operand).
    ("call", "int_str"): [("ValueError",
                           "(- 1" + "0" * 4300 + ") < {0} /\\ {0} < 1" + "0" * 4300)],
    # (#49) ROUTE #284 — a FORMAT SPEC not valid for the operand's type raises `ValueError`
    # whatever the value: `f"{x:s}"` / `f"{x:.2}"` on an int ("Unknown format code 's'",
    # "Precision not allowed in integer format specifier"), `f"{s:d}"` on a str. The
    # emitter decides a LITERAL spec at emit time against CPython's own `format()` (spec
    # validity is value-independent for int and str) and consults this row only for a spec
    # that is INVALID, or whose validity it cannot decide (a computed `{x:{w}}` spec, a
    # width/precision of more than 6 digits): the obligation is then `false`, so a
    # reachable occurrence under a `no_exception` covering `ValueError` never proves.
    ("call", "format_spec"): [("ValueError", "false")],
}


# (#49) ROUTE #285 — HOW EACH TRIGGERS ROW IS REACHED FROM AN EXPRESSION (the comprehension
# census). A comprehension / generator expression is lowered as an opaque value, so NONE of
# the obligations above is injected for its element, key, value, condition or iterable.
# `module6_whyml/functions.py::_reset_function_state` therefore refuses, under an active
# `no_exception` context, a comprehension containing an expression of one of the SHAPES
# listed for a row whose exception is active. The refusal is driven by THIS table: a row of
# TRIGGERS with no entry here makes EVERY comprehension refused under its exceptions
# (fail-closed for a row added later), and a row with an EMPTY shape list is reachable from a
# STATEMENT only (an element store / `del`), never from a comprehension's expressions.
# Shapes: ("BinOp", op) an IR BinOp with that op; ("Subscript", "") any subscript read;
# ("Call", name) a call of the bare builtin `name`; ("Method", name) a method call
# `<recv>.name(...)`; ("FString", "") an f-string with a part that is not a literal
# (an int part renders in decimal); ("FormattedValue", "") a `{v!c:spec}` part.
TRIGGER_EXPR_SHAPES: Dict[Tuple[str, Optional[str]], List[Tuple[str, str]]] = {
    ("binop", "div"): [("BinOp", "div")],
    ("binop", "mod"): [("BinOp", "mod")],
    ("binop", "/"): [("BinOp", "/")],
    ("binop", "//"): [("BinOp", "//")],
    ("binop", "%"): [("BinOp", "%")],
    ("binop", "<<"): [("BinOp", "<<")],
    ("binop", ">>"): [("BinOp", ">>")],
    ("binop", "**"): [("BinOp", "**")],
    ("subscript", "read"): [("Subscript", "")],
    ("subscript", "write"): [],
    ("subscript", "write_bytes"): [],
    ("subscript", "del"): [],
    ("call", "chr"): [("Call", "chr")],
    ("subscript", "read_str"): [("Subscript", "")],
    ("map_get", None): [("Subscript", "")],
    ("call", "divmod"): [("Call", "divmod")],
    ("attr_call", "pop"): [("Method", "pop")],
    ("attr_call", "index"): [("Method", "index")],
    ("call", "next"): [("Call", "next")],
    ("call", "int_str"): [("Call", "str"), ("Call", "repr"), ("Call", "format"),
                          ("Call", "print"), ("FString", ""), ("FormattedValue", ""),
                          ("BinOp", "%"), ("BinOp", "mod")],
    ("call", "format_spec"): [("FormattedValue", ""), ("Call", "format"),
                              ("Method", "format")],
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
