"""PyCSL error hierarchy with structured diagnostic fields.

Self-annotation seed (StdlibCoverage workplan PR 9, §9.1). The
``line`` field is non-negative; ``filename`` and ``stage`` are
strings (modeled as opaque ints for PyCSL). The class invariant
``self.line >= 0`` is enforced by `__init__` — the only mutator —
under the precondition that the caller passes a non-negative value.
"""


#@ class invariant self.line >= 0
class PyCSLError(Exception):
    """Base class for all PyCSL pipeline errors."""

    def __init__(self, message: str, *, filename: str = "", line: int = 0, stage: str = "") -> None:
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.stage = stage

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


class PyCSLParseError(PyCSLError):
    """Raised when a CSL contract string cannot be parsed (Module2)."""
    pass


class PyCSLSemanticError(PyCSLError):
    """Raised when a contract is semantically invalid (Module4)."""
    pass


class PyCSLIRError(PyCSLError):
    """Raised when an unsupported CSL node is encountered during IR emission (Module5)."""
    pass
