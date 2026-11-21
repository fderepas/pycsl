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

    def message(self) -> str:
        """The bare human message (no stage/file/line header, no code)."""
        return super().__str__()

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
