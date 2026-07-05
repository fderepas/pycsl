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

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict, Union

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
#
# "1.2" adds optional, default-valued FUNCTION fields `sibling_concrete` (bool),
# `verify_module` (str), `propagate_frame` (bool), `fresh_globals` (bool) — the
# allocator-frame / module-verification directives (#@ sibling_concrete,
# #@ verify_module, #@ propagate_frame, #@ fresh_globals) — and the optional
# TYPE-DECL field `init_ensures`. All default to False/"" so a "1.0"/"1.1" IR
# without them remains ingestable (additive MINOR bump); all three versions stay
# in ACCEPTED_IR_VERSIONS. See docs/ir.md §10.
#
# "1.3" (typing-engagement ty1 / 28-0000-typing-spec-4) adds the optional
# FUNCTION field `is_noreturn` (bool) — set true when the source declares
# `-> NoReturn` (PEP 484). The field is ABSENT on non-NoReturn functions (the
# emitter emits it only when true), so a "1.0"/"1.1"/"1.2" IR without it remains
# byte-identical and ingestable (additive MINOR bump); all four versions stay in
# ACCEPTED_IR_VERSIONS. Module 6 lowers `is_noreturn: true` to `ensures { false }`
# (NR1) and the non-vacuity gate (NR4) exempts the function from the vacuity
# probe. See docs/ir.md §10.
# "1.4" (typing-engagement ty3 / 33-1700-typing-spec-9) adds the optional TYPE-DECL
# field `type_params` and the optional FUNCTION field `type_params` — each a list of
# `{"name": str, "bound": Optional[str], "kind": str}` — set when a PEP 695 generic
# (`class C[T]:`, `def f[T]():`) or the legacy `TypeVar`/`Generic` spelling declares a
# type variable. The field is ABSENT on non-generic decls (emitted only when non-empty),
# so a "1.0"/"1.1"/"1.2"/"1.3" IR without it remains byte-identical and ingestable
# (additive MINOR bump); all five versions stay in ACCEPTED_IR_VERSIONS. The field is
# consumed by `frontend/monomorphize.apply_monomorphization` (the step-5 IR-resolution
# pass): COLLECT concrete instantiations, EMIT name-mangled specialized copies with
# substituted contracts, GT3/GT4 loud-fails. See docs/ir.md §10.
IR_VERSION = "1.4"
ACCEPTED_IR_VERSIONS = frozenset({"1.0", "1.1", "1.2", "1.3", "1.4"})


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
    # Optional (IR v1.3; typing-engagement ty1 / 28-0000-typing-spec-4): set true
    # when the source declares `-> NoReturn` (PEP 484). ABSENT on non-NoReturn
    # functions (emitted only when true → byte-identical for unaffected drivers).
    # Module 6 lowers it to `ensures { false }` (NR1); the non-vacuity gate
    # exempts the function from the vacuity probe (NR4). See docs/ir.md §5/§10.
    is_noreturn: bool
    # Optional (IR v1.4; typing-engagement ty3 / 33-1700-typing-spec-9): the type
    # parameters of a PEP 695 generic method/function (`def f[T]():`) or the legacy
    # `TypeVar`/`Generic` spelling. ABSENT on non-generic functions (emitted only when
    # non-empty → byte-identical for unaffected drivers). Consumed by
    # `frontend/monomorphize.apply_monomorphization` (the step-5 IR-resolution pass):
    # COLLECT concrete instantiations → EMIT name-mangled specialized copies with
    # substituted contracts. See docs/ir.md §10.
    type_params: List[Dict[str, Any]]


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
            f"IR must be a dict, got {type(ir).__name__}", stage=stage,
            code="PYCSL-IR-NOTDICT",
        )

    missing_top = _REQUIRED_TOP - ir.keys()
    if missing_top:
        raise PyCSLIRError(
            f"IR is missing top-level keys: {sorted(missing_top)}", stage=stage,
            code="PYCSL-IR-MISSINGTOP",
        )

    # IR-as-wire-format: the core declares the range of versions it ingests.
    # A stamped-but-unsupported version is a hard error (don't proceed to lower
    # an IR this core may misread); an unstamped IR is tolerated as legacy/internal
    # (the real pipeline's front-end always stamps it — see Module5).
    ir_version = ir.get("ir_version")
    if ir_version is not None and ir_version not in ACCEPTED_IR_VERSIONS:
        raise PyCSLIRError(
            f"unsupported ir_version {ir_version!r}; this core ingests "
            f"{sorted(ACCEPTED_IR_VERSIONS)}", stage=stage,
            code="PYCSL-IR-VERSION",
        )

    if not isinstance(ir["functions"], list):
        raise PyCSLIRError(
            "IR 'functions' must be a list", stage=stage,
            code="PYCSL-IR-FUNCSLIST",
        )

    for i, func in enumerate(ir["functions"]):
        if not isinstance(func, dict):
            raise PyCSLIRError(
                f"IR functions[{i}] must be a dict, got {type(func).__name__}",
                stage=stage,
                code="PYCSL-IR-FUNCDICT",
            )
        missing_func = _REQUIRED_FUNCTION - func.keys()
        if missing_func:
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' is missing IR keys: {sorted(missing_func)}",
                stage=stage,
                code="PYCSL-IR-MISSINGFUNC",
            )
        contracts = func.get("contracts")
        if not isinstance(contracts, dict):
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' contracts must be a dict", stage=stage,
                code="PYCSL-IR-CONTRACTSDICT",
            )
        missing_contracts = _REQUIRED_CONTRACTS - contracts.keys()
        if missing_contracts:
            name = func.get("name", f"<index {i}>")
            raise PyCSLIRError(
                f"Function '{name}' contracts missing keys: {sorted(missing_contracts)}",
                stage=stage,
                code="PYCSL-IR-MISSINGCONTRACTS",
            )


# ===========================================================================
# Typed sum-type IR schema (refactor.md / ir-schema-spec.md Phase A)
# ===========================================================================
# ADDITIVE layer: the JSON wire format (the `TypedDict` classes above and the
# `Dict[str, Any]` values Module5 emits / Module6 consumes) is UNCHANGED. These
# sum classes are the typed in-memory representation that Phase B will migrate
# the consumers onto one `_handle_*` method at a time. Nothing in the pipeline
# imports them yet — they are defined-but-unused (the standing gate stays
# byte-identical because the JSON output is untouched).
#
# The design is the standard "typed AST" pattern: one closed-sum base class per
# IR node category (`StmtIR` / `ExprIR`), one frozen-dataclass constructor per
# node kind, with concrete typed fields. `from_dict` / `to_dict` are the bridge
# between the JSON wire shape and the in-memory sum; `to_dict(from_dict(d))`
# round-trips every IR node (dict equality, see test_ir_schema_roundtrip.py).
#
# Contract expressions reuse `ExprIR`: the contract sub-language shares the
# `"type"`-keyed dict shape with value expressions (Forall / Exists / BinOp /
# Subscript / ... all appear in both `requires`/`ensures` and in body values),
# so a single ExprIR sum covers both. `ContractExprIR` is exported as an alias
# for readability at contract-conversion sites.
# ---------------------------------------------------------------------------

# Sentinel for "this key was absent in the source dict" — distinct from `None`,
# which the wire format uses as a real payload value (e.g. `Return.value` is
# emitted as JSON `null` when the source has `return` with no expression, and
# `ArraySliceSet.upper` is `null` for an open upper bound). `to_dict` emits a
# key only if its field is not `_ABSENT`, so the round-trip preserves both
# "absent key" and "present-but-null key" faithfully.
_ABSENT: Any = object()


@dataclass(frozen=True)
class IRNode:
    """Base for the typed IR sums. `kind` is the constructor tag (the wire
    string under the `"stmt"` or `"type"` key)."""
    kind: str

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# StmtIR — the closed sum for statement nodes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StmtIR(IRNode):
    """Base class for every IR statement constructor. The wire dict's
    `"stmt"` key becomes `kind`; the payload fields are typed."""
    def to_dict(self) -> Dict[str, Any]:
        return _stmt_to_dict(self)


@dataclass(frozen=True)
class AssignStmt(StmtIR):
    target: str
    value: "ExprIR"


@dataclass(frozen=True)
class AugAssignStmt(StmtIR):
    target: str
    op: str
    value: "ExprIR"


@dataclass(frozen=True)
class ArraySetStmt(StmtIR):
    array: "ExprIR"
    index: "ExprIR"
    value: "ExprIR"


@dataclass(frozen=True)
class DelSubscriptStmt(StmtIR):
    # wrong-lowering-to-fix.md §WL-05c (T7): `del d[k]` — a dict/set item deletion.
    # Module 6 lowers a LOCAL dict/set to `map_update_none` (faithful key clear) and a
    # dict/set PARAMETER to the WL-05 caller-visible-mutation rejection (fail-closed).
    array: "ExprIR"
    index: "ExprIR"


@dataclass(frozen=True)
class ArraySliceSetStmt(StmtIR):
    array: "ExprIR"
    lower: "ExprIR"
    upper: Optional["ExprIR"]
    value: "ExprIR"


@dataclass(frozen=True)
class IfStmt(StmtIR):
    test: "ExprIR"
    body: List["StmtIR"]
    orelse: List["StmtIR"]


@dataclass(frozen=True)
class WhileStmt(StmtIR):
    line: int
    test: "ExprIR"
    invariants: List["ExprIR"]
    variants: List["ExprIR"]
    body: List["StmtIR"]


@dataclass(frozen=True)
class ForStmt(StmtIR):
    line: int
    target: str
    iter: "ExprIR"
    invariants: List["ExprIR"]
    variants: List["ExprIR"]
    body: List["StmtIR"]
    allow_iteration_mutation: bool
    lineno: int


@dataclass(frozen=True)
class ReturnStmt(StmtIR):
    value: Optional["ExprIR"]


@dataclass(frozen=True)
class ExprStmt(StmtIR):
    value: "ExprIR"


@dataclass(frozen=True)
class TryStmt(StmtIR):
    body: List["StmtIR"]
    handlers: List[Dict[str, Any]]
    orelse: List["StmtIR"]
    finalbody: List["StmtIR"]


@dataclass(frozen=True)
class MatchStmt(StmtIR):
    subject: "ExprIR"
    cases: List[Dict[str, Any]]


@dataclass(frozen=True)
class CriticalSectionStmt(StmtIR):
    mutex: str
    body: List["StmtIR"]
    assume_invariant: Optional["ExprIR"]
    prove_invariant: Optional["ExprIR"]


@dataclass(frozen=True)
class FieldAssignStmt(StmtIR):
    object: str
    field: str
    value: "ExprIR"


@dataclass(frozen=True)
class FieldAugAssignStmt(StmtIR):
    object: str
    field: str
    op: str
    value: "ExprIR"


@dataclass(frozen=True)
class TupleUnpackStmt(StmtIR):
    targets: List[str]
    value: "ExprIR"


@dataclass(frozen=True)
class GhostAssignStmt(StmtIR):
    target: str
    value: "ExprIR"
    op: str
    ghost_type: str


@dataclass(frozen=True)
class GhostArraySetStmt(StmtIR):
    target: str
    index: "ExprIR"
    value: "ExprIR"


@dataclass(frozen=True)
class LabelStmt(StmtIR):
    name: str


@dataclass(frozen=True)
class RaiseStmt(StmtIR):
    exc_type: Optional[str]
    exc_value: Optional["ExprIR"]


@dataclass(frozen=True)
class AssertStmt(StmtIR):
    test: "ExprIR"
    msg: str = _ABSENT  # type: ignore[assignment]


@dataclass(frozen=True)
class PassStmt(StmtIR):
    pass


@dataclass(frozen=True)
class BreakStmt(StmtIR):
    pass


@dataclass(frozen=True)
class ContinueStmt(StmtIR):
    pass


@dataclass(frozen=True)
class ProofAssertStmt(StmtIR):
    assert_kind: str  # "assert" (prove-and-assume) or "check" (prove-and-discard)
    test: "ExprIR"
    origin: str = _ABSENT  # type: ignore[assignment]


@dataclass(frozen=True)
class OpaqueStmt(StmtIR):
    """Fallback for stmt kinds without an explicit typed class (preserves the
    raw dict so `to_dict(from_dict(d)) == d` holds for every IR node, including
    ones Phase A has not yet classed). Phase B will replace these as it
    migrates each `_handle_*` consumer."""
    raw: Dict[str, Any]


# ---------------------------------------------------------------------------
# ExprIR — the closed sum for expression nodes (value + contract expressions)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExprIR(IRNode):
    """Base class for every IR expression constructor. The wire dict's `"type"`
    key becomes `kind`; payload fields are typed. Contract expressions
    (`requires` / `ensures` / `assigns` / `raises` / loop invariants / proof
    asserts) share this sum — see `ContractExprIR`."""

    def to_dict(self) -> Dict[str, Any]:
        return _expr_to_dict(self)


# --- Literals & references -------------------------------------------------

@dataclass(frozen=True)
class NumberExpr(ExprIR):
    value: Any  # int or float


@dataclass(frozen=True)
class StringExpr(ExprIR):
    value: str


@dataclass(frozen=True)
class BoolExpr(ExprIR):
    value: bool


@dataclass(frozen=True)
class NoneExpr(ExprIR):
    pass


@dataclass(frozen=True)
class VarExpr(ExprIR):
    name: str


@dataclass(frozen=True)
class ResultExpr(ExprIR):
    pass


@dataclass(frozen=True)
class RawWhymlExpr(ExprIR):
    whyml: str


@dataclass(frozen=True)
class UnknownPyExprExpr(ExprIR):
    pass


@dataclass(frozen=True)
class NothingExpr(ExprIR):
    pass


# --- Operators ------------------------------------------------------------

@dataclass(frozen=True)
class BinOpExpr(ExprIR):
    op: str
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class UnaryOpExpr(ExprIR):
    op: str
    expr: "ExprIR"


@dataclass(frozen=True)
class StrConcatExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class StarredExpr(ExprIR):
    value: "ExprIR"


# --- Container / attribute access ----------------------------------------

@dataclass(frozen=True)
class SubscriptExpr(ExprIR):
    value: "ExprIR"
    index: "ExprIR"


@dataclass(frozen=True)
class SliceExpr(ExprIR):
    lower: "ExprIR"
    upper: "ExprIR"
    step: Any


@dataclass(frozen=True)
class FieldGetExpr(ExprIR):
    object: Any  # str ("self") or var name; not a nested ExprIR in the wire format
    field: str


@dataclass(frozen=True)
class AttributeExpr(ExprIR):
    object: "ExprIR"
    attr: str


@dataclass(frozen=True)
class CallExpr(ExprIR):
    func: str
    args: List["ExprIR"]
    receiver: "ExprIR" = _ABSENT  # type: ignore[assignment]


@dataclass(frozen=True)
class TupleExpr(ExprIR):
    elts: List["ExprIR"]


@dataclass(frozen=True)
class ArrayLitExpr(ExprIR):
    elts: List["ExprIR"]


@dataclass(frozen=True)
class DictLitExpr(ExprIR):
    keys: List["ExprIR"]
    values: List["ExprIR"]


@dataclass(frozen=True)
class ListCompExpr(ExprIR):
    elt: "ExprIR"
    generators: List[Any]


@dataclass(frozen=True)
class DictCompExpr(ExprIR):
    key: "ExprIR"
    value: "ExprIR"
    generators: List[Any]


@dataclass(frozen=True)
class SetCompExpr(ExprIR):
    elt: "ExprIR"
    generators: List[Any]


# --- Quantifiers & contract-only expressions ------------------------------

@dataclass(frozen=True)
class ForallExpr(ExprIR):
    var: str
    body: "ExprIR"
    binder_type: str = _ABSENT  # type: ignore[assignment]


@dataclass(frozen=True)
class ExistsExpr(ExprIR):
    var: str
    body: "ExprIR"
    binder_type: str = _ABSENT  # type: ignore[assignment]


@dataclass(frozen=True)
class ForallItemsExpr(ExprIR):
    key: str
    val: str
    map: str
    body: "ExprIR"


@dataclass(frozen=True)
class MapValueIsExpr(ExprIR):
    map: str
    key: "ExprIR"
    value: "ExprIR"


@dataclass(frozen=True)
class OldFieldExpr(ExprIR):
    object: str
    field: str


@dataclass(frozen=True)
class OldExpr(ExprIR):
    expr: "ExprIR"


@dataclass(frozen=True)
class AtExpr(ExprIR):
    expr: "ExprIR"
    label: str


@dataclass(frozen=True)
class IfExprExpr(ExprIR):
    test: "ExprIR"
    body: "ExprIR"
    orelse: "ExprIR"


@dataclass(frozen=True)
class NamedExprExpr(ExprIR):
    target: str
    value: "ExprIR"


# --- Misc / rare ---------------------------------------------------------

@dataclass(frozen=True)
class ArrayLenExpr(ExprIR):
    var: str


@dataclass(frozen=True)
class InGlobalsExpr(ExprIR):
    name: str


@dataclass(frozen=True)
class InScopeExpr(ExprIR):
    name: str


@dataclass(frozen=True)
class AssignsRegionExpr(ExprIR):
    base: str
    low: "ExprIR"
    high: "ExprIR"


@dataclass(frozen=True)
class ValidExpr(ExprIR):
    base: str
    length: "ExprIR"


@dataclass(frozen=True)
class SeparatedExpr(ExprIR):
    base1: str
    len1: "ExprIR"
    base2: str
    len2: "ExprIR"


@dataclass(frozen=True)
class Length2DExpr(ExprIR):
    base: str
    rows: "ExprIR"
    cols: "ExprIR"


@dataclass(frozen=True)
class Valid2DExpr(ExprIR):
    base: str
    row: "ExprIR"
    col: "ExprIR"


@dataclass(frozen=True)
class IsSortedExpr(ExprIR):
    base: str
    lo: "ExprIR"
    hi: "ExprIR"


@dataclass(frozen=True)
class ArrayEqExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class PermutationExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class SumExpr(ExprIR):
    base: str
    lo: "ExprIR"
    hi: "ExprIR"


@dataclass(frozen=True)
class SliceAccessExpr(ExprIR):
    value: "ExprIR"
    slice: "ExprIR"


@dataclass(frozen=True)
class FStringExpr(ExprIR):
    parts: List["ExprIR"]


@dataclass(frozen=True)
class LambdaExpr(ExprIR):
    params: List[str]
    body: "ExprIR"


@dataclass(frozen=True)
class SetLitExpr(ExprIR):
    elts: List["ExprIR"]


@dataclass(frozen=True)
class MkTupleExpr(ExprIR):
    elts: List["ExprIR"]


@dataclass(frozen=True)
class FstExprExpr(ExprIR):
    tuple: "ExprIR"


@dataclass(frozen=True)
class SndExprExpr(ExprIR):
    tuple: "ExprIR"


@dataclass(frozen=True)
class ProjExprExpr(ExprIR):
    tuple: "ExprIR"
    index: int


@dataclass(frozen=True)
class CtorTestExpr(ExprIR):
    var: str
    ctor: str


@dataclass(frozen=True)
class CtorPayloadExpr(ExprIR):
    var: str
    ctor: str
    index: int


@dataclass(frozen=True)
class StrLengthExpr(ExprIR):
    string: "ExprIR"


@dataclass(frozen=True)
class StrSubExpr(ExprIR):
    string: "ExprIR"
    lo: "ExprIR"
    hi: "ExprIR"


@dataclass(frozen=True)
class GhostCopyExpr(ExprIR):
    arr: str


@dataclass(frozen=True)
class GhostCopyRangeExpr(ExprIR):
    arr: str
    lo: "ExprIR"
    hi: "ExprIR"


@dataclass(frozen=True)
class GhostMakeExpr(ExprIR):
    size: "ExprIR"
    default: "ExprIR"


@dataclass(frozen=True)
class MapEmptyExpr(ExprIR):
    pass


@dataclass(frozen=True)
class MapGetExpr(ExprIR):
    dict: "ExprIR"
    key: "ExprIR"


@dataclass(frozen=True)
class MapSetExpr(ExprIR):
    dict: "ExprIR"
    key: "ExprIR"
    value: "ExprIR"


@dataclass(frozen=True)
class MapEqExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class HasKeyExpr(ExprIR):
    dict: "ExprIR"
    key: "ExprIR"


@dataclass(frozen=True)
class MapRemoveExpr(ExprIR):
    dict: "ExprIR"
    key: "ExprIR"


@dataclass(frozen=True)
class SetEmptyExpr(ExprIR):
    pass


@dataclass(frozen=True)
class SetAddExpr(ExprIR):
    set: "ExprIR"
    elem: "ExprIR"


@dataclass(frozen=True)
class SetRemoveExpr(ExprIR):
    set: "ExprIR"
    elem: "ExprIR"


@dataclass(frozen=True)
class SetMemExpr(ExprIR):
    elem: "ExprIR"
    set: "ExprIR"


@dataclass(frozen=True)
class SetUnionExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class SetInterExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class SetDiffExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class SetCardExpr(ExprIR):
    set: "ExprIR"
    lo: "ExprIR"
    hi: "ExprIR"


@dataclass(frozen=True)
class SetSubsetExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class SetEqExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class NilExpr(ExprIR):
    pass


@dataclass(frozen=True)
class ConsExpr(ExprIR):
    head: "ExprIR"
    tail: "ExprIR"


@dataclass(frozen=True)
class HdExpr(ExprIR):
    list: "ExprIR"


@dataclass(frozen=True)
class TlExpr(ExprIR):
    list: "ExprIR"


@dataclass(frozen=True)
class ListLengthExpr(ExprIR):
    list: "ExprIR"


@dataclass(frozen=True)
class NthExpr(ExprIR):
    list: "ExprIR"
    index: "ExprIR"


@dataclass(frozen=True)
class MemExpr(ExprIR):
    elem: "ExprIR"
    list: "ExprIR"


@dataclass(frozen=True)
class AppendExpr(ExprIR):
    left: "ExprIR"
    right: "ExprIR"


@dataclass(frozen=True)
class OpaqueExpr(ExprIR):
    """Fallback for expr kinds without an explicit typed class. Preserves the
    raw dict so round-trip holds for every IR node (including ones Phase A has
    not yet classed)."""
    raw: Dict[str, Any]


# Contract expressions share the ExprIR sum (same `"type"`-keyed wire shape).
ContractExprIR = ExprIR


# ---------------------------------------------------------------------------
# from_dict — wire dict → typed sum
# ---------------------------------------------------------------------------

def _e(d: Any) -> "ExprIR":
    """Coerce a dict (or scalar) into an ExprIR. `None`/absent → NoneExpr."""
    if d is None:
        return NoneExpr(kind="None")
    if isinstance(d, dict):
        return expr_from_dict(d)
    # A bare scalar (shouldn't happen for a well-formed IR) — wrap opaquely.
    return OpaqueExpr(kind="Opaque", raw={"type": "Opaque", "value": d})


def _es(items: List[Any]) -> List["ExprIR"]:
    return [_e(x) for x in items]


def _ss(items: List[Any]) -> List["StmtIR"]:
    return [stmt_from_dict(x) for x in items if isinstance(x, dict)]


def stmt_from_dict(d: Dict[str, Any]) -> StmtIR:
    """Convert a wire-format stmt dict into its typed `StmtIR` constructor.

    Falls back to `OpaqueStmt` (preserving the raw dict) for any stmt kind
    without an explicit typed class, or for a node carrying extra attribution
    keys (e.g. `act_name`) the typed class does not model — so the round-trip
    holds for every IR node.
    """
    node = _stmt_from_dict_inner(d)
    if isinstance(node, (OpaqueStmt,)):
        return node
    # If the typed node drops keys present in the source dict (extra
    # attribution like `act_name`, or a future field not yet classed),
    # fall back to opaque so `to_dict(from_dict(d)) == d` holds.
    if set(_stmt_to_dict(node).keys()) != set(d.keys()):
        return OpaqueStmt(kind=node.kind, raw=dict(d))
    return node


def _stmt_from_dict_inner(d: Dict[str, Any]) -> StmtIR:
    k = d.get("stmt", "")
    if k == "Assign":
        return AssignStmt(kind=k, target=d["target"], value=_e(d.get("value")))
    if k == "AugAssign":
        return AugAssignStmt(kind=k, target=d["target"], op=d.get("op", ""),
                              value=_e(d.get("value")))
    if k == "ArraySet":
        return ArraySetStmt(kind=k, array=_e(d.get("array")),
                            index=_e(d.get("index")), value=_e(d.get("value")))
    if k == "DelSubscript":
        return DelSubscriptStmt(kind=k, array=_e(d.get("array")),
                                index=_e(d.get("index")))
    if k == "ArraySliceSet":
        up = d.get("upper")
        return ArraySliceSetStmt(kind=k, array=_e(d.get("array")),
                                 lower=_e(d.get("lower")),
                                 upper=_e(up) if up is not None else None,
                                 value=_e(d.get("value")))
    if k == "If":
        return IfStmt(kind=k, test=_e(d.get("test")),
                      body=_ss(d.get("body", [])), orelse=_ss(d.get("orelse", [])))
    if k == "While":
        return WhileStmt(kind=k, line=d.get("line", 0), test=_e(d.get("test")),
                         invariants=_es(d.get("invariants", [])),
                         variants=_es(d.get("variants", [])),
                         body=_ss(d.get("body", [])))
    if k == "For":
        return ForStmt(kind=k, line=d.get("line", 0), target=d.get("target", ""),
                       iter=_e(d.get("iter")),
                       invariants=_es(d.get("invariants", [])),
                       variants=_es(d.get("variants", [])),
                       body=_ss(d.get("body", [])),
                       allow_iteration_mutation=d.get("allow_iteration_mutation", False),
                       lineno=d.get("lineno", 0))
    if k == "Return":
        v = d.get("value")
        return ReturnStmt(kind=k, value=_e(v) if v is not None else None)
    if k == "Expr":
        return ExprStmt(kind=k, value=_e(d.get("value")))
    if k == "Try":
        return TryStmt(kind=k, body=_ss(d.get("body", [])),
                       handlers=d.get("handlers", []),
                       orelse=_ss(d.get("orelse", [])),
                       finalbody=_ss(d.get("finalbody", [])))
    if k == "Match":
        return MatchStmt(kind=k, subject=_e(d.get("subject")),
                         cases=d.get("cases", []))
    if k == "CriticalSection":
        ai = d.get("assume_invariant")
        pi = d.get("prove_invariant")
        return CriticalSectionStmt(kind=k, mutex=d.get("mutex", ""),
                                   body=_ss(d.get("body", [])),
                                   assume_invariant=_e(ai) if ai is not None else None,
                                   prove_invariant=_e(pi) if pi is not None else None)
    if k == "FieldAssign":
        return FieldAssignStmt(kind=k, object=d.get("object", "self"),
                               field=d.get("field", ""), value=_e(d.get("value")))
    if k == "FieldAugAssign":
        return FieldAugAssignStmt(kind=k, object=d.get("object", "self"),
                                  field=d.get("field", ""), op=d.get("op", ""),
                                  value=_e(d.get("value")))
    if k == "TupleUnpack":
        return TupleUnpackStmt(kind=k, targets=d.get("targets", []),
                               value=_e(d.get("value")))
    if k == "GhostAssign":
        return GhostAssignStmt(kind=k, target=d.get("target", ""),
                               value=_e(d.get("value")),
                               op=d.get("op", "="),
                               ghost_type=d.get("ghost_type", "int"))
    if k == "GhostArraySet":
        return GhostArraySetStmt(kind=k, target=d.get("target", ""),
                                 index=_e(d.get("index")),
                                 value=_e(d.get("value")))
    if k == "Label":
        return LabelStmt(kind=k, name=d.get("name", ""))
    if k == "Raise":
        ev = d.get("exc_value")
        return RaiseStmt(kind=k, exc_type=d.get("exc_type"),
                         exc_value=_e(ev) if ev is not None else None)
    if k == "Assert":
        msg = d.get("msg", _ABSENT)
        return AssertStmt(kind=k, test=_e(d.get("test")),
                          msg=msg if msg is not _ABSENT else _ABSENT)
    if k == "Pass":
        return PassStmt(kind=k)
    if k == "Break":
        return BreakStmt(kind=k)
    if k == "Continue":
        return ContinueStmt(kind=k)
    if k == "ProofAssert":
        origin = d.get("origin", _ABSENT)
        return ProofAssertStmt(kind=k, assert_kind=d.get("kind", "assert"),
                               test=_e(d.get("test")),
                               origin=origin if origin is not _ABSENT else _ABSENT)
    return OpaqueStmt(kind=k or "Opaque", raw=dict(d))


def expr_from_dict(d: Dict[str, Any]) -> ExprIR:
    """Convert a wire-format expr dict into its typed `ExprIR` constructor.

    Falls back to `OpaqueExpr` (preserving the raw dict) for any expr kind
    without an explicit typed class, or for a node carrying extra attribution
    keys (e.g. `act_name`) the typed class does not model — so the round-trip
    holds for every IR node.
    """
    node = _expr_from_dict_inner(d)
    if isinstance(node, (OpaqueExpr,)):
        return node
    if set(_expr_to_dict(node).keys()) != set(d.keys()):
        return OpaqueExpr(kind=node.kind, raw=dict(d))
    return node


def _expr_from_dict_inner(d: Dict[str, Any]) -> ExprIR:
    k = d.get("type", "")
    if k == "Number":
        return NumberExpr(kind=k, value=d.get("value"))
    if k == "String":
        return StringExpr(kind=k, value=d.get("value", ""))
    if k == "Bool":
        return BoolExpr(kind=k, value=d.get("value"))
    if k == "None":
        return NoneExpr(kind=k)
    if k == "Var":
        return VarExpr(kind=k, name=d.get("name", ""))
    if k == "Result":
        return ResultExpr(kind=k)
    if k == "RawWhyml":
        return RawWhymlExpr(kind=k, whyml=d.get("whyml", ""))
    if k == "UnknownPyExpr":
        return UnknownPyExprExpr(kind=k)
    if k == "Nothing":
        return NothingExpr(kind=k)
    if k == "BinOp":
        return BinOpExpr(kind=k, op=d.get("op", ""),
                        left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "UnaryOp":
        return UnaryOpExpr(kind=k, op=d.get("op", ""), expr=_e(d.get("expr")))
    if k == "StrConcat":
        return StrConcatExpr(kind=k, left=_e(d.get("left")),
                             right=_e(d.get("right")))
    if k == "Starred":
        return StarredExpr(kind=k, value=_e(d.get("value")))
    if k == "Subscript":
        return SubscriptExpr(kind=k, value=_e(d.get("value")),
                             index=_e(d.get("index")))
    if k == "Slice":
        return SliceExpr(kind=k, lower=_e(d.get("lower")), upper=_e(d.get("upper")), step=d.get("step"))
    if k == "FieldGet":
        return FieldGetExpr(kind=k, object=d.get("object"),
                            field=d.get("field", ""))
    if k == "Attribute":
        return AttributeExpr(kind=k, object=_e(d.get("object")),
                            attr=d.get("attr", ""))
    if k == "Call":
        rec = d.get("receiver", _ABSENT)
        return CallExpr(kind=k, func=d.get("func", ""), args=_es(d.get("args", [])),
                        receiver=_e(rec) if rec is not _ABSENT else _ABSENT)
    if k == "Tuple":
        return TupleExpr(kind=k, elts=_es(d.get("elts", [])))
    if k == "ArrayLit":
        return ArrayLitExpr(kind=k, elts=_es(d.get("elts", [])))
    if k == "DictLit":
        return DictLitExpr(kind=k,
                           keys=[expr_from_dict(x) for x in d.get("keys", [])],
                           values=[expr_from_dict(x) for x in d.get("values", [])])
    if k == "ListComp":
        return ListCompExpr(kind=k, elt=expr_from_dict(d["elt"]),
                            generators=d.get("generators", []))
    if k == "DictComp":
        return DictCompExpr(kind=k, key=expr_from_dict(d["key"]),
                            value=expr_from_dict(d["value"]),
                            generators=d.get("generators", []))
    if k == "SetComp":
        return SetCompExpr(kind=k, elt=expr_from_dict(d["elt"]),
                           generators=d.get("generators", []))
    if k == "Forall":
        bt = d.get("binder_type", _ABSENT)
        return ForallExpr(kind=k, var=d.get("var", ""), body=_e(d.get("body")),
                          binder_type=bt if bt is not _ABSENT else _ABSENT)
    if k == "Exists":
        bt = d.get("binder_type", _ABSENT)
        return ExistsExpr(kind=k, var=d.get("var", ""), body=_e(d.get("body")),
                          binder_type=bt if bt is not _ABSENT else _ABSENT)
    if k == "ForallItems":
        return ForallItemsExpr(kind=k, key=d.get("key", ""), val=d.get("val", ""),
                               map=d.get("map", ""), body=_e(d.get("body")))
    if k == "MapValueIs":
        return MapValueIsExpr(kind=k, map=d.get("map", ""),
                              key=_e(d.get("key")), value=_e(d.get("value")))
    if k == "OldField":
        return OldFieldExpr(kind=k, object=d.get("object"), field=d.get("field", ""))
    if k == "Old":
        return OldExpr(kind=k, expr=_e(d.get("expr")))
    if k == "At":
        return AtExpr(kind=k, expr=_e(d.get("expr")), label=d.get("label", ""))
    if k == "IfExpr":
        return IfExprExpr(kind=k, test=_e(d.get("test")),
                          body=_e(d.get("body")), orelse=_e(d.get("orelse")))
    if k == "NamedExpr":
        return NamedExprExpr(kind=k, target=d.get("target", ""),
                             value=_e(d.get("value")))
    if k == "ArrayLen":
        return ArrayLenExpr(kind=k, var=d.get("var", ""))
    if k == "InGlobals":
        return InGlobalsExpr(kind=k, name=d.get("name", ""))
    if k == "InScope":
        return InScopeExpr(kind=k, name=d.get("name", ""))
    if k == "AssignsRegion":
        return AssignsRegionExpr(kind=k, base=d.get("base", ""),
                                 low=_e(d.get("low")), high=_e(d.get("high")))
    if k == "Valid":
        return ValidExpr(kind=k, base=d.get("base", ""), length=_e(d.get("length")))
    if k == "Separated":
        return SeparatedExpr(kind=k, base1=d.get("base1", ""), len1=_e(d.get("len1")),
                             base2=d.get("base2", ""), len2=_e(d.get("len2")))
    if k == "Length2D":
        return Length2DExpr(kind=k, base=d.get("base", ""), rows=_e(d.get("rows")), cols=_e(d.get("cols")))
    if k == "Valid2D":
        return Valid2DExpr(kind=k, base=d.get("base", ""), row=_e(d.get("row")), col=_e(d.get("col")))
    if k == "IsSorted":
        return IsSortedExpr(kind=k, base=d.get("base", ""), lo=_e(d.get("lo")), hi=_e(d.get("hi")))
    if k == "ArrayEq":
        return ArrayEqExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "Permutation":
        return PermutationExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "Sum":
        return SumExpr(kind=k, base=d.get("base", ""), lo=_e(d.get("lo")), hi=_e(d.get("hi")))
    if k == "SliceAccess":
        return SliceAccessExpr(kind=k, value=_e(d.get("value")), slice=_e(d.get("slice")))
    if k == "FString":
        return FStringExpr(kind=k, parts=_es(d.get("parts", [])))
    if k == "Lambda":
        return LambdaExpr(kind=k, params=d.get("params", []),
                         body=_e(d.get("body")))
    if k == "SetLit":
        return SetLitExpr(kind=k, elts=_es(d.get("elts", [])))
    if k == "MkTuple":
        return MkTupleExpr(kind=k, elts=_es(d.get("elts", [])))
    if k == "FstExpr":
        return FstExprExpr(kind=k, tuple=_e(d.get("tuple")))
    if k == "SndExpr":
        return SndExprExpr(kind=k, tuple=_e(d.get("tuple")))
    if k == "ProjExpr":
        return ProjExprExpr(kind=k, tuple=_e(d.get("tuple")),
                           index=d.get("index", 0))
    if k == "CtorTest":
        return CtorTestExpr(kind=k, var=d.get("var", ""), ctor=d.get("ctor", ""))
    if k == "CtorPayload":
        return CtorPayloadExpr(kind=k, var=d.get("var", ""), ctor=d.get("ctor", ""),
                               index=d.get("index", 0))
    if k == "StrLength":
        return StrLengthExpr(kind=k, string=_e(d.get("string")))
    if k == "StrSub":
        return StrSubExpr(kind=k, string=_e(d.get("string")),
                          lo=_e(d.get("lo")), hi=_e(d.get("hi")))
    if k == "GhostCopy":
        return GhostCopyExpr(kind=k, arr=d.get("arr", ""))
    if k == "GhostCopyRange":
        return GhostCopyRangeExpr(kind=k, arr=d.get("arr", ""),
                                  lo=_e(d.get("lo")), hi=_e(d.get("hi")))
    if k == "GhostMake":
        return GhostMakeExpr(kind=k, size=_e(d.get("size")), default=_e(d.get("default")))
    if k == "MapEmpty":
        return MapEmptyExpr(kind=k)
    if k == "MapGet":
        return MapGetExpr(kind=k, dict=_e(d.get("dict")), key=_e(d.get("key")))
    if k == "MapSet":
        return MapSetExpr(kind=k, dict=_e(d.get("dict")), key=_e(d.get("key")),
                          value=_e(d.get("value")))
    if k == "MapEq":
        return MapEqExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "HasKey":
        return HasKeyExpr(kind=k, dict=_e(d.get("dict")), key=_e(d.get("key")))
    if k == "MapRemove":
        return MapRemoveExpr(kind=k, dict=_e(d.get("dict")), key=_e(d.get("key")))
    if k == "SetEmpty":
        return SetEmptyExpr(kind=k)
    if k == "SetAdd":
        return SetAddExpr(kind=k, set=_e(d.get("set")), elem=_e(d.get("elem")))
    if k == "SetRemove":
        return SetRemoveExpr(kind=k, set=_e(d.get("set")), elem=_e(d.get("elem")))
    if k == "SetMem":
        return SetMemExpr(kind=k, elem=_e(d.get("elem")), set=_e(d.get("set")))
    if k == "SetUnion":
        return SetUnionExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "SetInter":
        return SetInterExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "SetDiff":
        return SetDiffExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "SetCard":
        return SetCardExpr(kind=k, set=_e(d.get("set")), lo=_e(d.get("lo")), hi=_e(d.get("hi")))
    if k == "SetSubset":
        return SetSubsetExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "SetEq":
        return SetEqExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    if k == "Nil":
        return NilExpr(kind=k)
    if k == "Cons":
        return ConsExpr(kind=k, head=_e(d.get("head")), tail=_e(d.get("tail")))
    if k == "Hd":
        return HdExpr(kind=k, list=_e(d.get("list")))
    if k == "Tl":
        return TlExpr(kind=k, list=_e(d.get("list")))
    if k == "ListLength":
        return ListLengthExpr(kind=k, list=_e(d.get("list")))
    if k == "Nth":
        return NthExpr(kind=k, list=_e(d.get("list")), index=_e(d.get("index")))
    if k == "Mem":
        return MemExpr(kind=k, elem=_e(d.get("elem")), list=_e(d.get("list")))
    if k == "Append":
        return AppendExpr(kind=k, left=_e(d.get("left")), right=_e(d.get("right")))
    return OpaqueExpr(kind=k or "Opaque", raw=dict(d))


def from_dict(d: Dict[str, Any]) -> Union[StmtIR, ExprIR]:
    """Auto-detecting converter: a `"stmt"`-keyed dict → `StmtIR`, a
    `"type"`-keyed dict → `ExprIR`. Prefer `stmt_from_dict` / `expr_from_dict`
    when the category is known."""
    if "stmt" in d:
        return stmt_from_dict(d)
    return expr_from_dict(d)


# ---------------------------------------------------------------------------
# to_dict — typed sum → wire dict (inverse of from_dict)
# ---------------------------------------------------------------------------

def _opt_e(v: Optional[ExprIR]) -> Optional[Dict[str, Any]]:
    return v.to_dict() if v is not None else None


def _opt_o(v: Any) -> Any:
    """Map the `_ABSENT` sentinel back to itself (caller checks); otherwise
    unwrap an ExprIR/StmtIR to its dict, or pass scalars through."""
    if v is _ABSENT:
        return v
    if isinstance(v, IRNode):
        return v.to_dict()
    if isinstance(v, list):
        return [_opt_o(x) for x in v]
    return v


def _stmt_to_dict(s: StmtIR) -> Dict[str, Any]:
    """Inverse of `stmt_from_dict`. Emits the canonical wire shape: the
    `"stmt"` tag first, then each payload key. Optional keys whose field is
    `_ABSENT` are omitted; present-but-`None` keys (e.g. `Return.value: null`)
    are emitted as JSON null — matching Module5's emission."""
    if isinstance(s, OpaqueStmt):
        return dict(s.raw)
    out: Dict[str, Any] = {"stmt": s.kind}
    if isinstance(s, AssignStmt):
        out["target"] = s.target
        out["value"] = s.value.to_dict()
    elif isinstance(s, AugAssignStmt):
        out["target"] = s.target
        out["op"] = s.op
        out["value"] = s.value.to_dict()
    elif isinstance(s, ArraySetStmt):
        out["array"] = s.array.to_dict()
        out["index"] = s.index.to_dict()
        out["value"] = s.value.to_dict()
    elif isinstance(s, DelSubscriptStmt):
        out["array"] = s.array.to_dict()
        out["index"] = s.index.to_dict()
    elif isinstance(s, ArraySliceSetStmt):
        out["array"] = s.array.to_dict()
        out["lower"] = s.lower.to_dict()
        out["upper"] = s.upper.to_dict() if s.upper is not None else None
        out["value"] = s.value.to_dict()
    elif isinstance(s, IfStmt):
        out["test"] = s.test.to_dict()
        out["body"] = [b.to_dict() for b in s.body]
        out["orelse"] = [b.to_dict() for b in s.orelse]
    elif isinstance(s, WhileStmt):
        out["line"] = s.line
        out["test"] = s.test.to_dict()
        out["invariants"] = [i.to_dict() for i in s.invariants]
        out["variants"] = [v.to_dict() for v in s.variants]
        out["body"] = [b.to_dict() for b in s.body]
    elif isinstance(s, ForStmt):
        out["line"] = s.line
        out["target"] = s.target
        out["iter"] = s.iter.to_dict()
        out["invariants"] = [i.to_dict() for i in s.invariants]
        out["variants"] = [v.to_dict() for v in s.variants]
        out["body"] = [b.to_dict() for b in s.body]
        out["allow_iteration_mutation"] = s.allow_iteration_mutation
        out["lineno"] = s.lineno
    elif isinstance(s, ReturnStmt):
        out["value"] = s.value.to_dict() if s.value is not None else None
    elif isinstance(s, ExprStmt):
        out["value"] = s.value.to_dict()
    elif isinstance(s, TryStmt):
        out["body"] = [b.to_dict() for b in s.body]
        out["handlers"] = s.handlers
        out["orelse"] = [b.to_dict() for b in s.orelse]
        out["finalbody"] = [b.to_dict() for b in s.finalbody]
    elif isinstance(s, MatchStmt):
        out["subject"] = s.subject.to_dict()
        out["cases"] = s.cases
    elif isinstance(s, CriticalSectionStmt):
        out["mutex"] = s.mutex
        out["body"] = [b.to_dict() for b in s.body]
        out["assume_invariant"] = (s.assume_invariant.to_dict()
                                   if s.assume_invariant is not None else None)
        out["prove_invariant"] = (s.prove_invariant.to_dict()
                                  if s.prove_invariant is not None else None)
    elif isinstance(s, FieldAssignStmt):
        out["object"] = s.object
        out["field"] = s.field
        out["value"] = s.value.to_dict()
    elif isinstance(s, FieldAugAssignStmt):
        out["object"] = s.object
        out["field"] = s.field
        out["op"] = s.op
        out["value"] = s.value.to_dict()
    elif isinstance(s, TupleUnpackStmt):
        out["targets"] = s.targets
        out["value"] = s.value.to_dict()
    elif isinstance(s, GhostAssignStmt):
        out["target"] = s.target
        out["value"] = s.value.to_dict()
        out["op"] = s.op
        out["ghost_type"] = s.ghost_type
    elif isinstance(s, GhostArraySetStmt):
        out["target"] = s.target
        out["index"] = s.index.to_dict()
        out["value"] = s.value.to_dict()
    elif isinstance(s, LabelStmt):
        out["name"] = s.name
    elif isinstance(s, RaiseStmt):
        out["exc_type"] = s.exc_type
        out["exc_value"] = s.exc_value.to_dict() if s.exc_value is not None else None
    elif isinstance(s, AssertStmt):
        out["test"] = s.test.to_dict()
        if s.msg is not _ABSENT:
            out["msg"] = s.msg
    elif isinstance(s, PassStmt):
        pass
    elif isinstance(s, BreakStmt):
        pass
    elif isinstance(s, ContinueStmt):
        pass
    elif isinstance(s, ProofAssertStmt):
        # `ProofAssertStmt.assert_kind` carries the assert/check sub-kind (the
        # wire `kind` key); the dataclass `kind` field (from IRNode) carries
        # the node tag "ProofAssert". Emit both faithfully.
        out["kind"] = s.assert_kind
        out["test"] = s.test.to_dict()
        if s.origin is not _ABSENT:
            out["origin"] = s.origin
    return out


def _expr_to_dict(e: ExprIR) -> Dict[str, Any]:
    """Inverse of `expr_from_dict`. Emits the canonical wire shape: the
    `"type"` tag first, then each payload key. Optional keys whose field is
    `_ABSENT` are omitted."""
    if isinstance(e, OpaqueExpr):
        return dict(e.raw)
    out: Dict[str, Any] = {"type": e.kind}
    if isinstance(e, NumberExpr):
        out["value"] = e.value
    elif isinstance(e, StringExpr):
        out["value"] = e.value
    elif isinstance(e, BoolExpr):
        out["value"] = e.value
    elif isinstance(e, NoneExpr):
        pass
    elif isinstance(e, VarExpr):
        out["name"] = e.name
    elif isinstance(e, ResultExpr):
        pass
    elif isinstance(e, RawWhymlExpr):
        out["whyml"] = e.whyml
    elif isinstance(e, UnknownPyExprExpr):
        pass
    elif isinstance(e, NothingExpr):
        pass
    elif isinstance(e, BinOpExpr):
        out["op"] = e.op
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, UnaryOpExpr):
        out["op"] = e.op
        out["expr"] = e.expr.to_dict()
    elif isinstance(e, StrConcatExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, StarredExpr):
        out["value"] = e.value.to_dict()
    elif isinstance(e, SubscriptExpr):
        out["value"] = e.value.to_dict()
        out["index"] = e.index.to_dict()
    elif isinstance(e, SliceExpr):
        out["lower"] = e.lower.to_dict()
        out["upper"] = e.upper.to_dict()
        out["step"] = e.step
    elif isinstance(e, FieldGetExpr):
        out["object"] = e.object
        out["field"] = e.field
    elif isinstance(e, AttributeExpr):
        out["object"] = e.object.to_dict()
        out["attr"] = e.attr
    elif isinstance(e, CallExpr):
        out["func"] = e.func
        out["args"] = [a.to_dict() for a in e.args]
        if e.receiver is not _ABSENT:
            out["receiver"] = e.receiver.to_dict()
    elif isinstance(e, TupleExpr):
        out["elts"] = [x.to_dict() for x in e.elts]
    elif isinstance(e, ArrayLitExpr):
        out["elts"] = [x.to_dict() for x in e.elts]
    elif isinstance(e, DictLitExpr):
        out["keys"] = [x.to_dict() for x in e.keys]
        out["values"] = [x.to_dict() for x in e.values]
    elif isinstance(e, ListCompExpr):
        out["elt"] = e.elt.to_dict()
        out["generators"] = e.generators
    elif isinstance(e, DictCompExpr):
        out["key"] = e.key.to_dict()
        out["value"] = e.value.to_dict()
        out["generators"] = e.generators
    elif isinstance(e, SetCompExpr):
        out["elt"] = e.elt.to_dict()
        out["generators"] = e.generators
    elif isinstance(e, ForallExpr):
        out["var"] = e.var
        if e.binder_type is not _ABSENT:
            out["binder_type"] = e.binder_type
        out["body"] = e.body.to_dict()
    elif isinstance(e, ExistsExpr):
        out["var"] = e.var
        if e.binder_type is not _ABSENT:
            out["binder_type"] = e.binder_type
        out["body"] = e.body.to_dict()
    elif isinstance(e, ForallItemsExpr):
        out["key"] = e.key
        out["val"] = e.val
        out["map"] = e.map
        out["body"] = e.body.to_dict()
    elif isinstance(e, MapValueIsExpr):
        out["map"] = e.map
        out["key"] = e.key.to_dict()
        out["value"] = e.value.to_dict()
    elif isinstance(e, OldFieldExpr):
        out["object"] = e.object
        out["field"] = e.field
    elif isinstance(e, OldExpr):
        out["expr"] = e.expr.to_dict()
    elif isinstance(e, AtExpr):
        out["expr"] = e.expr.to_dict()
        out["label"] = e.label
    elif isinstance(e, IfExprExpr):
        out["test"] = e.test.to_dict()
        out["body"] = e.body.to_dict()
        out["orelse"] = e.orelse.to_dict()
    elif isinstance(e, NamedExprExpr):
        out["target"] = e.target
        out["value"] = e.value.to_dict()
    elif isinstance(e, ArrayLenExpr):
        out["var"] = e.var
    elif isinstance(e, InGlobalsExpr):
        out["name"] = e.name
    elif isinstance(e, InScopeExpr):
        out["name"] = e.name
    elif isinstance(e, AssignsRegionExpr):
        out["base"] = e.base
        out["low"] = e.low.to_dict()
        out["high"] = e.high.to_dict()
    elif isinstance(e, ValidExpr):
        out["base"] = e.base
        out["length"] = e.length.to_dict()
    elif isinstance(e, SeparatedExpr):
        out["base1"] = e.base1
        out["len1"] = e.len1.to_dict()
        out["base2"] = e.base2
        out["len2"] = e.len2.to_dict()
    elif isinstance(e, Length2DExpr):
        out["base"] = e.base
        out["rows"] = e.rows.to_dict()
        out["cols"] = e.cols.to_dict()
    elif isinstance(e, Valid2DExpr):
        out["base"] = e.base
        out["row"] = e.row.to_dict()
        out["col"] = e.col.to_dict()
    elif isinstance(e, IsSortedExpr):
        out["base"] = e.base
        out["lo"] = e.lo.to_dict()
        out["hi"] = e.hi.to_dict()
    elif isinstance(e, ArrayEqExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, PermutationExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, SumExpr):
        out["base"] = e.base
        out["lo"] = e.lo.to_dict()
        out["hi"] = e.hi.to_dict()
    elif isinstance(e, SliceAccessExpr):
        out["value"] = e.value.to_dict()
        out["slice"] = e.slice.to_dict()
    elif isinstance(e, FStringExpr):
        out["parts"] = [p.to_dict() for p in e.parts]
    elif isinstance(e, LambdaExpr):
        out["params"] = e.params
        out["body"] = e.body.to_dict()
    elif isinstance(e, SetLitExpr):
        out["elts"] = [x.to_dict() for x in e.elts]
    elif isinstance(e, MkTupleExpr):
        out["elts"] = [x.to_dict() for x in e.elts]
    elif isinstance(e, FstExprExpr):
        out["tuple"] = e.tuple.to_dict()
    elif isinstance(e, SndExprExpr):
        out["tuple"] = e.tuple.to_dict()
    elif isinstance(e, ProjExprExpr):
        out["tuple"] = e.tuple.to_dict()
        out["index"] = e.index
    elif isinstance(e, CtorTestExpr):
        out["var"] = e.var
        out["ctor"] = e.ctor
    elif isinstance(e, CtorPayloadExpr):
        out["var"] = e.var
        out["ctor"] = e.ctor
        out["index"] = e.index
    elif isinstance(e, StrLengthExpr):
        out["string"] = e.string.to_dict()
    elif isinstance(e, StrSubExpr):
        out["string"] = e.string.to_dict()
        out["lo"] = e.lo.to_dict()
        out["hi"] = e.hi.to_dict()
    elif isinstance(e, GhostCopyExpr):
        out["arr"] = e.arr
    elif isinstance(e, GhostCopyRangeExpr):
        out["arr"] = e.arr
        out["lo"] = e.lo.to_dict()
        out["hi"] = e.hi.to_dict()
    elif isinstance(e, GhostMakeExpr):
        out["size"] = e.size.to_dict()
        out["default"] = e.default.to_dict()
    elif isinstance(e, MapEmptyExpr):
        pass
    elif isinstance(e, MapGetExpr):
        out["dict"] = e.dict.to_dict()
        out["key"] = e.key.to_dict()
    elif isinstance(e, MapSetExpr):
        out["dict"] = e.dict.to_dict()
        out["key"] = e.key.to_dict()
        out["value"] = e.value.to_dict()
    elif isinstance(e, MapEqExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, HasKeyExpr):
        out["dict"] = e.dict.to_dict()
        out["key"] = e.key.to_dict()
    elif isinstance(e, MapRemoveExpr):
        out["dict"] = e.dict.to_dict()
        out["key"] = e.key.to_dict()
    elif isinstance(e, SetEmptyExpr):
        pass
    elif isinstance(e, SetAddExpr):
        out["set"] = e.set.to_dict()
        out["elem"] = e.elem.to_dict()
    elif isinstance(e, SetRemoveExpr):
        out["set"] = e.set.to_dict()
        out["elem"] = e.elem.to_dict()
    elif isinstance(e, SetMemExpr):
        out["elem"] = e.elem.to_dict()
        out["set"] = e.set.to_dict()
    elif isinstance(e, SetUnionExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, SetInterExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, SetDiffExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, SetCardExpr):
        out["set"] = e.set.to_dict()
        out["lo"] = e.lo.to_dict()
        out["hi"] = e.hi.to_dict()
    elif isinstance(e, SetSubsetExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, SetEqExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    elif isinstance(e, NilExpr):
        pass
    elif isinstance(e, ConsExpr):
        out["head"] = e.head.to_dict()
        out["tail"] = e.tail.to_dict()
    elif isinstance(e, HdExpr):
        out["list"] = e.list.to_dict()
    elif isinstance(e, TlExpr):
        out["list"] = e.list.to_dict()
    elif isinstance(e, ListLengthExpr):
        out["list"] = e.list.to_dict()
    elif isinstance(e, NthExpr):
        out["list"] = e.list.to_dict()
        out["index"] = e.index.to_dict()
    elif isinstance(e, MemExpr):
        out["elem"] = e.elem.to_dict()
        out["list"] = e.list.to_dict()
    elif isinstance(e, AppendExpr):
        out["left"] = e.left.to_dict()
        out["right"] = e.right.to_dict()
    return out


def to_dict(node: Union[StmtIR, ExprIR]) -> Dict[str, Any]:
    """Inverse of `from_dict`: serialize a typed `StmtIR`/`ExprIR` node back to
    its wire-format dict. `to_dict(from_dict(d)) == d` holds for every IR node
    (dict equality — key order is not preserved, only keys/values)."""
    return node.to_dict()


__all__ = [
    # Existing TypedDict layer
    "ContractsIR", "FunctionIR", "ProgramIR", "validate_ir",
    "IR_VERSION", "ACCEPTED_IR_VERSIONS",
    # Typed sum schema (Phase A)
    "IRNode", "StmtIR", "ExprIR", "ContractExprIR",
    # Stmt constructors
    "AssignStmt", "AugAssignStmt", "ArraySetStmt", "ArraySliceSetStmt",
    "IfStmt", "WhileStmt", "ForStmt", "ReturnStmt", "ExprStmt", "TryStmt",
    "MatchStmt", "CriticalSectionStmt", "FieldAssignStmt", "FieldAugAssignStmt",
    "TupleUnpackStmt", "GhostAssignStmt", "GhostArraySetStmt", "LabelStmt",
    "RaiseStmt", "AssertStmt", "PassStmt", "BreakStmt", "ContinueStmt",
    "ProofAssertStmt", "OpaqueStmt",
    # Expr constructors
    "NumberExpr", "StringExpr", "BoolExpr", "NoneExpr", "VarExpr", "ResultExpr",
    "RawWhymlExpr", "UnknownPyExprExpr", "NothingExpr", "BinOpExpr", "UnaryOpExpr",
    "StrConcatExpr", "StarredExpr", "SubscriptExpr", "SliceExpr", "FieldGetExpr",
    "AttributeExpr", "CallExpr", "TupleExpr", "ArrayLitExpr", "DictLitExpr",
    "ListCompExpr", "DictCompExpr", "SetCompExpr", "ForallExpr", "ExistsExpr",
    "ForallItemsExpr", "MapValueIsExpr", "OldFieldExpr", "OldExpr", "AtExpr",
    "IfExprExpr", "NamedExprExpr", "ArrayLenExpr", "InGlobalsExpr", "InScopeExpr",
    "AssignsRegionExpr", "ValidExpr", "SeparatedExpr", "Length2DExpr",
    "Valid2DExpr", "IsSortedExpr", "ArrayEqExpr", "PermutationExpr", "SumExpr",
    "SliceAccessExpr", "FStringExpr", "LambdaExpr", "SetLitExpr", "MkTupleExpr",
    "FstExprExpr", "SndExprExpr", "ProjExprExpr", "CtorTestExpr",
    "CtorPayloadExpr", "StrLengthExpr", "StrSubExpr", "GhostCopyExpr",
    "GhostCopyRangeExpr", "GhostMakeExpr", "MapEmptyExpr", "MapGetExpr",
    "MapSetExpr", "MapEqExpr", "HasKeyExpr", "MapRemoveExpr", "SetEmptyExpr",
    "SetAddExpr", "SetRemoveExpr", "SetMemExpr", "SetUnionExpr", "SetInterExpr",
    "SetDiffExpr", "SetCardExpr", "SetSubsetExpr", "SetEqExpr", "NilExpr",
    "ConsExpr", "HdExpr", "TlExpr", "ListLengthExpr", "NthExpr", "MemExpr",
    "AppendExpr", "OpaqueExpr",
    # Converters
    "from_dict", "stmt_from_dict", "expr_from_dict", "to_dict",
]
