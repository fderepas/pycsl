"""PyCSL error hierarchy with structured diagnostic fields.

Self-annotation seed (StdlibCoverage workplan PR 9, §9.1). The
``line`` field is non-negative; ``filename`` and ``stage`` are
strings (modeled as the Why3 `string.String` value type). The class invariant
``self.line >= 0`` is enforced by `__init__` — the only mutator —
under the precondition that the caller passes a non-negative value.
"""


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

    def as_dict(self) -> dict:
        """Structured, machine-readable view of this diagnostic.

        Returns ``{code, stage, filename, line, message}``. The ``message`` is the
        bare human message (identical to what callers have always matched); the
        ``code`` is the new structural field (empty string if unassigned)."""
        return {
            "code": self.code,
            "stage": self.stage,
            "filename": self.filename,
            "line": self.line,
            "message": self.message(),
        }


class PyCSLParseError(PyCSLError):
    """Raised when a CSL contract string cannot be parsed (Module2)."""
    pass


class PyCSLSemanticError(PyCSLError):
    """Raised when a contract is semantically invalid (Module4)."""
    pass


class PyCSLIRError(PyCSLError):
    """Raised when an unsupported CSL node is encountered during IR emission (Module5)."""
    pass
