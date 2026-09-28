"""PyCSL error hierarchy with structured diagnostic fields.

Self-annotation seed (StdlibCoverage workplan PR 9, §9.1). The
``line`` field is non-negative; ``filename`` and ``stage`` are
strings (modeled as the Why3 `string.String` value type). The class invariant
``self.line >= 0`` is enforced by `__init__` — the only mutator —
under the precondition that the caller passes a non-negative value.
"""
from typing import Any, Dict

# (#49) gen #32 — `PyVal` SELECTS THE CERTIFIED HETEROGENEOUS VALUE MODEL. `as_dict`
# returns `{code: str, stage: str, filename: str, line: int, message: str}` — a
# HETEROGENEOUS dict — and the emitter infers ONE value type per map, so with no
# annotation it chose `map int (option int)` and Why3 rejected the three string fields.
# This file is member #1 of `bin/run-self-annotation-suite.sh` and had been the suite's
# only failure since the diagnostics feature landed, unobserved because that oracle had
# no scheduled runner until window #8.
# `Dict[str, PyVal]` selects the `hval` sum (HStr | HInt | HArr | HMap | HNode), proven
# axiom-free by the fable oracle and co-landed with the Rocq/Lean Phase2f_PyVal cert, so
# each value is tagged by its real kind instead of erased to an int. MEASURED: the
# codomain is selected from a DECLARED LOCAL or PARAM and NOT from a return annotation
# (backlog #69), which is why the literal is bound to `_d` before being returned.
# `PyVal = Any` at runtime, so nothing about the returned dict changes.
PyVal = Any


#@ class invariant self.line >= 0
class PyCSLError(Exception):
    """Base class for all PyCSL pipeline errors."""

    def __init__(self, message: str, *, filename: str = "", line: int = 0, stage: str = "",
                 code: str = "") -> None:
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.stage = stage
        # Stable, machine-readable diagnostic code (e.g. "PYCSL-SEM-RESULT").
        # CRITICAL: this is a *structural-only* field — it is deliberately NOT
        # rendered by __str__, so the human-facing message stays byte-identical to
        # the pre-code text that negative drivers and refactor gates match against.
        # Machine consumers read it via `.code` / `.as_dict()` / `--diagnostics-json`.
        self.code = code

    # (#49) gen #31 — THE MARKER CAME OFF, and the reason it carried had gone stale a day
    # earlier. It said the string-typed self fields were "carried as ints in the record
    # model" and named a REOPENING CAPABILITY. They are not: `preamble.py`'s TP-3 Gap 6
    # maps a `str` field to a Why3 `string`, and this session's `self.f = <annotated
    # __init__ param>` repair gives the un-annotated ones the parameter's type — so the
    # record has read `mutable pycslerror_filename: string` for some time.
    # What actually blocked it was three unrelated one-rule gaps, each measured
    # load-bearing by ablation and each landed with this conversion: a string FIELD had no
    # TRUTHINESS rule (`if self.stage:`), `<x>.__str__()` lowered to a `string` val but was
    # not CLASSIFIED as string-valued (`msg = super().__str__()`), and the string-local
    # fixpoint ran before the pass that makes `" ".join(parts)` string-typed.
    # The body now lowers faithfully — `str_concat_op`/`str_join_seq`/`str_length_op` over
    # real `string` fields, no int hash anywhere — and the four frame `ensures` that the
    # abstract `val` merely ASSUMED are PROVED. Retiring it converts FOUR emitted symbols,
    # not one: the three subclasses inherit `__str__` and each had its own `val`.
    # See getting-better/open-routes/finding-the-field-value-model-already-landed.md
    def __str__(self) -> str:
        parts = []
        if self.stage:
            parts.append(f"[{self.stage}]")
        if self.filename:
            parts.append(self.filename)
            if self.line:
                parts.append(f"line {self.line}")
        header = " ".join(parts)
        msg = super().__str__()
        return f"{header}: {msg}" if header else msg

    # super().__str__() is opaque (Exception base); returns string but PyCSL cannot see that
    # (#49) gen #32 — `#@ sibling_concrete` BECAUSE `as_dict` NOW CALLS THIS. Converting `as_dict`
    # made `self.message()` a live intra-class call site, and the DEFAULT lowering for such a call
    # is a receiver-less abstract `val self_message_0` whose result is unconstrained — so
    # `check-shadowed-selfcalls` went 14 -> 15 with "a conversion landed whose body no caller can
    # see". That is the honest complaint: `as_dict` would have been proved while the one entry of
    # its map that comes from a method call stayed invisible. The marker is the sanctioned opt-in
    # (Module2 `SiblingConcrete`: "an intra-class `self.<m>()` call to THIS method is lowered to a
    # CONCRETE call, so the caller gets the real method's full contract"), and this is exactly the
    # documented use — a cheap leaf whose guarantee the caller absorbs as an atom. The ratchet is
    # NOT raised; the cause is fixed.
    #@ sibling_concrete
    def message(self) -> str:
        """The bare human message (no stage/file/line header, no code)."""
        return super().__str__()

    # (#49) gen #32 — CONVERTED. This was `#@ \trusted reviewer: pycsl-self-annotate` with the
    # comment "builds a dict (PyCSL cannot model dict construction here yet)", and that comment
    # is what went out of date: the certified heterogeneous `hval` model selected by
    # `Dict[str, PyVal]` models exactly this dict, so the body proves instead of being assumed.
    # The live twin needed the same change for a different reason — it was the self-annotation
    # suite's only FAILURE — so one repair both retires a marker here and turns that oracle green.
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def as_dict(self) -> Dict[str, PyVal]:
        """Structured, machine-readable view of this diagnostic.

        Returns ``{code, stage, filename, line, message}``. The ``message`` is the
        bare human message (identical to what callers have always matched); the
        ``code`` is the new structural field (empty string if unassigned)."""
        _d: Dict[str, PyVal] = {
            "code": self.code,
            "stage": self.stage,
            "filename": self.filename,
            "line": self.line,
            "message": self.message(),
        }
        return _d


class PyCSLParseError(PyCSLError):
    """Raised when a CSL contract string cannot be parsed (Module2)."""
    pass


class PyCSLSemanticError(PyCSLError):
    """Raised when a contract is semantically invalid (Module4)."""
    pass


class PyCSLIRError(PyCSLError):
    """Raised when an unsupported CSL node is encountered during IR emission (Module5)."""
    pass
