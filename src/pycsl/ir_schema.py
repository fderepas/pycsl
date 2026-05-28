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
    # Required at runtime (validated by validate_ir):
    type_decls: List[Dict[str, Any]]
    functions: List[FunctionIR]
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
