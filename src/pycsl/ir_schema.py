"""TypedDict definitions and runtime validation for the PyCSL JSON IR.

The IR flows from Module5 (emitter) to Module6 (transpiler).  This module
provides:
  - TypedDict types that document the expected shape of the IR dict.
  - ``validate_ir(ir)`` — a lightweight structural check that raises
    ``PyCSLIRError`` on any missing required key so mistakes are caught
    immediately after emission rather than causing mysterious failures inside
    the transpiler.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict

from errors import PyCSLIRError


# ---------------------------------------------------------------------------
# IR version — the IR is a wire format between a (per-language) front-end and
# the language-agnostic core (pycsl-language-agnostic-core-spec.md §5; refactor.md
# Phase A). It is stamped with a semantic version and a source-language tag so the
# core can refuse an IR it does not understand instead of failing mysteriously
# downstream.
#
# Compatibility policy (semver-style): MINOR bumps are ADDITIVE (new optional
# keys/nodes a newer core still ingests); MAJOR bumps are BREAKING (a removed or
# re-meaning'd key). `ACCEPTED_IR_VERSIONS` is the exact set this core ingests;
# widen it as additive versions land, and drop a major when support ends.
# ---------------------------------------------------------------------------

# "1.1" (refactor.md Phase C/C1) adds the optional top-level `imports` key —
# the module's import list, consumed by pycsl._resolve_imports so multi-file
# resolution is a pure IR→IR pass. Additive (MINOR bump): "1.0" IRs remain
# ingestable, so both versions stay in ACCEPTED_IR_VERSIONS.
IR_VERSION = "1.1"
ACCEPTED_IR_VERSIONS = frozenset({"1.0", "1.1"})


# ---------------------------------------------------------------------------
# TypedDict schema (documentation + static type-checker support)
# ---------------------------------------------------------------------------

# total=False because TypedDict with Required/NotRequired requires Python 3.11;
# runtime validation is handled by validate_ir() below.

class ContractsIR(TypedDict, total=False):
    """contracts sub-dict inside a FunctionIR."""
    requires: List[Dict[str, Any]]
    ensures: List[Dict[str, Any]]
    assigns: List[Dict[str, Any]]
    raises: List[Dict[str, Any]]
    # `no_exception` (Phase 1 NoException workplan). Both fields are
    # optional; absence is semantically equivalent to no_exception: []
    # plus no_exception_all: False (ambient mode, today's default).
    no_exception: List[str]
    no_exception_all: bool


class FunctionIR(TypedDict, total=False):
    """One entry in program_ir["functions"]."""
    # §4.4 source span (line/col of the function in the original source) — lets the
    # core report IR-level semantic errors against the source; see refactor.md Phase B.
    line: int
    col: int
    # Required at runtime (validated by validate_ir):
    name: str
    symbol_table: Dict[str, str]
    return_annotation: str
    contracts: ContractsIR
    body: List[Dict[str, Any]]
    function_variants: List[Dict[str, Any]]
    diverges: bool
    trusted: bool
    bounded_int: Optional[int]
    # Optional:
    pure: bool
    array2d_params: List[str]
    array1d_params: List[str]
    kind: str
    self_type: str


class ProgramIR(TypedDict, total=False):
    """Top-level JSON IR produced by Module5 and consumed by Module6."""
    # Interface stamp (the IR-as-wire-format contract; see IR_VERSION above):
    ir_version: str         # semantic version of the IR schema this document conforms to
    source_language: str    # the front-end that produced it ("python" today)
    # Required at runtime (validated by validate_ir):
    type_decls: List[Dict[str, Any]]
    functions: List[FunctionIR]
    # Optional (IR v1.1; refactor.md Phase C/C1): the module's import list,
    # each entry [local, original, module, level, is_module]. Consumed by
    # pycsl._resolve_imports for multi-file resolution; Module6 ignores it.
    imports: List[List[Any]]
    # Optional concurrency keys (present when --memory-model concurrent):
    shared_vars: List[Dict[str, Any]]
    mutex_invariants: Dict[str, Dict[str, Any]]
    thread_entries: List[str]
    lock_order: List[str]


# ---------------------------------------------------------------------------
# Required key sets
# ---------------------------------------------------------------------------

_REQUIRED_TOP = {"type_decls", "functions"}

_REQUIRED_FUNCTION = {
    "name",
    "symbol_table",
    "return_annotation",
    "contracts",
    "body",
    "function_variants",
    "diverges",
    "trusted",
    "bounded_int",
}

_REQUIRED_CONTRACTS = {"requires", "ensures", "assigns", "raises"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_ir(ir: Any, *, stage: str = "ir-validate") -> None:
    """Raise PyCSLIRError if *ir* is missing required top-level or per-function keys.

    Performs only structural (key-presence) validation — does not type-check
    individual node dicts, which would be too expensive for the hot path.
    """
    if not isinstance(ir, dict):
        raise PyCSLIRError(
            f"IR must be a dict, got {type(ir).__name__}", stage=stage
        )

    missing_top = _REQUIRED_TOP - ir.keys()
    if missing_top:
        raise PyCSLIRError(
            f"IR is missing top-level keys: {sorted(missing_top)}", stage=stage
        )

    # IR-as-wire-format: the core declares the range of versions it ingests.
    # A stamped-but-unsupported version is a hard error (don't proceed to lower
    # an IR this core may misread); an unstamped IR is tolerated as legacy/internal
    # (the real pipeline's front-end always stamps it — see Module5).
    ir_version = ir.get("ir_version")
    if ir_version is not None and ir_version not in ACCEPTED_IR_VERSIONS:
        raise PyCSLIRError(
            f"unsupported ir_version {ir_version!r}; this core ingests "
            f"{sorted(ACCEPTED_IR_VERSIONS)}", stage=stage
        )

    if not isinstance(ir["functions"], list):
        raise PyCSLIRError(
            "IR 'functions' must be a list", stage=stage
        )

    for i, func in enumerate(ir["functions"]):
        if not isinstance(func, dict):
            raise PyCSLIRError(
                f"IR functions[{i}] must be a dict, got {type(func).__name__}",
                stage=stage,
            )
        missing_func = _REQUIRED_FUNCTION - func.keys()
        if missing_func:
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' is missing IR keys: {sorted(missing_func)}",
                stage=stage,
            )
        contracts = func.get("contracts")
        if not isinstance(contracts, dict):
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' contracts must be a dict", stage=stage
            )
        missing_contracts = _REQUIRED_CONTRACTS - contracts.keys()
        if missing_contracts:
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' contracts missing keys: {sorted(missing_contracts)}",
                stage=stage,
            )
