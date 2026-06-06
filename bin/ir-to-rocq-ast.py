#!/usr/bin/env python3
"""ir-to-rocq-ast.py — Convert Module 5 IR JSON to a Rocq `whyml_stmt`
literal (OCaml syntax) for use by the CC.5 byte-diff driver.

This is the foundational piece of the Q4 IR-bridge work, scoped to a
"simple subset" of PyCSL programs. The subset handles:

  - Statement IR shapes:
      Pass, Assign (with simple-expr RHS), AugAssign (with int op),
      ArraySet (with Var array), and their sequences.
  - Expression IR shapes:
      Number, Var, BinOp(+/-/*//), Subscript(Var,_), Call(len, [Var])
      and UnaryOp(-).

It REJECTS (with a clear diagnostic):
  - Boolean comparisons in expressions (<, <=, ==, !=, etc.) —
    the formal `expr` type has no comparison constructor.
  - Function calls other than len() — formal expr has no call.
  - String literals, lists, dicts, sets — formal expr is int-typed.
  - Control flow at statement level (If, While, For, Try, ...) —
    these are tractable but defer to a future iteration of the
    converter; the formal `whyml_stmt` HAS these constructors but
    their bodies use the simple-subset stmts, so adding control
    flow requires extending the converter to call itself recursively
    on the body.
  - Return at any nesting (formal model maps Return to a WSeq+WAssign+
    WRaise pattern that diverges from Module 6's body-level emission).
    The byte-diff CONVENTION is to extract the body excluding any
    trailing Return.

Usage:
    bin/ir-to-rocq-ast.py <source.py>
        Reads PyCSL source, runs Module 5, converts the first
        function's body (excluding trailing Return), prints an
        OCaml expression of type `whyml_stmt` to stdout.

    Exit 0 on success, 2 if the body falls outside the simple subset
    (with a diagnostic explaining which IR shape was encountered).

Caller responsibility: the emitted OCaml expression is meant to be
spliced into a driver template (extraction/reference-driver.ml.in)
which links against the extracted EmitExtract.ml. The driver then
calls `emit_stmt_state_aware` on the constructed AST and prints the
result for diff against Module 6's output.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent

# WhyML reserved keywords — Module 6's `whyml_ident` (identifiers.py:24-35)
# prefixes these with `py_`. Our formal pretty-printer doesn't do this
# renaming, so we reject identifiers that would collide. See
# `bin/ir-to-rocq-ast.py` HEADER for the limitation.
_WHYML_RESERVED = {
    "at", "any", "diverges", "val", "let", "in", "if", "then", "else",
    "while", "do", "done", "for", "to", "begin", "end", "match", "with",
    "try", "raise", "exception", "type", "use", "module", "theory",
    "import", "export", "clone", "goal", "lemma", "axiom", "predicate",
    "function", "constant", "mutable", "ghost", "invariant", "variant",
    "requires", "ensures", "returns", "raises", "reads", "writes",
    "assert", "assume", "check", "absurd", "true", "false", "not",
    "old", "ref", "abstract", "private", "model", "range",
    "float", "by", "so", "pure", "alias", "label", "epsilon",
    "exists", "forall", "rec", "and", "or", "mod", "div", "result",
}


def _check_ident(name: str) -> None:
    if name in _WHYML_RESERVED:
        raise NotInSimpleSubset(
            f"identifier '{name}' is a WhyML reserved keyword "
            f"(Module 6 renames to 'py_{name}'; formal pretty-printer "
            f"doesn't do this sanitization)")


# --------------------------------------------------------------------
# Identifier escaping for OCaml string literals.
# --------------------------------------------------------------------

def ocaml_char_list(s: str) -> str:
    """Render a Python string as an OCaml `char list` literal — matches
    the extracted `ident = char list` type. We use the helper
    `to_char_list` from driver.ml to keep this readable.
    """
    return f'(to_char_list {json.dumps(s)})'


def ocaml_ident(name: str) -> str:
    """Wrap an identifier as an OCaml char_list literal, checking that
    it's not a WhyML reserved keyword. Use this for ALL identifiers
    (variable names, target names, array names, etc.) emitted into
    the Rocq AST. """
    _check_ident(name)
    return ocaml_char_list(name)


# --------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------

class NotInSimpleSubset(Exception):
    """Raised when an IR shape isn't supported by the v1 converter."""


# --------------------------------------------------------------------
# Expression conversion
# --------------------------------------------------------------------

BINOP_MAP = {"+": "OpAdd", "-": "OpSub", "*": "OpMul", "/": "OpDiv",
             "//": "OpDiv"}

# Python/IR comparison operators → formal cmpop constructors.
CMPOP_MAP = {"==": "OpEq", "!=": "OpNe",
             "<": "OpLt", "<=": "OpLe",
             ">": "OpGt", ">=": "OpGe"}


def conv_expr(e: Dict[str, Any]) -> str:
    """IR expression → OCaml expression of type `expr`.
    OCaml-extracted constructors take tuples: `Foo (a, b, c)`. """
    t = e.get("type")
    if t == "Number":
        v = e["value"]
        return f"(EInt {int(v)})"
    if t == "Var":
        return f"(EVar {ocaml_ident(e['name'])})"
    if t == "UnaryOp" and e.get("op") == "-":
        return f"(ENeg {conv_expr(e['operand'])})"
    if t == "BinOp":
        op = e.get("op")
        if op in BINOP_MAP:
            return (f"(EBinOp ({BINOP_MAP[op]}, "
                    f"{conv_expr(e['left'])}, {conv_expr(e['right'])}))")
        if op in CMPOP_MAP:
            return (f"(ECmp ({CMPOP_MAP[op]}, "
                    f"{conv_expr(e['left'])}, {conv_expr(e['right'])}))")
        raise NotInSimpleSubset(
            f"BinOp '{op}' not in formal binop/cmpop sets")
    if t == "Compare":
        # Module 5 sometimes emits Compare instead of BinOp for chained
        # comparisons. We only support 2-operand chains; reject longer.
        ops = e.get("ops", [])
        comparators = e.get("comparators", [])
        if len(ops) == 1 and len(comparators) == 1:
            op = ops[0]
            if op in CMPOP_MAP:
                return (f"(ECmp ({CMPOP_MAP[op]}, "
                        f"{conv_expr(e['left'])}, "
                        f"{conv_expr(comparators[0])}))")
        raise NotInSimpleSubset(
            f"Compare with ops={ops} not in simple subset")
    if t == "Subscript":
        val = e["value"]
        if val.get("type") != "Var":
            raise NotInSimpleSubset(
                "Subscript only supported on Var (formal ESubscript "
                "takes an ident)")
        return (f"(ESubscript ({ocaml_char_list(val['name'])}, "
                f"{conv_expr(e['index'])}))")
    if t == "Call":
        if e.get("func") == "len" and len(e.get("args", [])) == 1:
            arg = e["args"][0]
            if arg.get("type") != "Var":
                raise NotInSimpleSubset(
                    "len() argument must be a Var (formal ELen takes an ident)")
            return f"(ELen {ocaml_char_list(arg['name'])})"
        raise NotInSimpleSubset(
            f"Call to '{e.get('func')}' not in simple subset")
    raise NotInSimpleSubset(f"expression type '{t}' not in simple subset")


# --------------------------------------------------------------------
# Statement conversion
# --------------------------------------------------------------------

AUG_OP_MAP = {"+": "OpAdd", "-": "OpSub", "*": "OpMul", "/": "OpDiv"}

# IR augassign op → formal aug_op (no division).
GHOST_AUG_OP_MAP = {"+=": "AugAdd", "-=": "AugSub", "*=": "AugMul"}

# IR ghost_type → formal ghost_type. Matches Module 6's
# _resolve_effective_ghost_type output names.
GHOST_TYPE_MAP = {
    "int":        "GTInt",
    "string":     "GTString",
    "array":      "GTArray",
    "ghost_dict": "GTDict",
    "ghost_list": "GTList",
    "ghost_set":  "GTSet",
    "tuple2":     "GTTuple2",
    "tuple3":     "GTTuple3",
    "tuple4":     "GTTuple4",
}

# IR comparison op → contract_expr comparison constructor.
CONTRACT_CMP_MAP = {"==": "CEq", "!=": "CNe",
                    "<": "CLt", "<=": "CLe",
                    ">": "CGt", ">=": "CGe"}

# IR boolean op → contract_expr logical constructor.
CONTRACT_LOGIC_MAP = {"and": "CAnd", "or": "COr"}


def conv_contract_expr(e: Dict[str, Any]) -> str:
    """IR contract-shaped expression → OCaml `contract_expr` literal.
    Subset: literals, vars, arithmetic, comparisons, logic, length,
    subscript, Result. """
    t = e.get("type")
    if t == "Number":
        return f"(CInt {int(e['value'])})"
    if t == "Var":
        return f"(CVar {ocaml_ident(e['name'])})"
    if t == "Result":
        return "CResult"
    if t == "Length":
        return f"(CLength {ocaml_char_list(e['name'])})"
    if t == "Subscript":
        v = e["value"]
        if v.get("type") != "Var":
            raise NotInSimpleSubset(
                "contract Subscript only on Var")
        return (f"(CSubscript ({ocaml_char_list(v['name'])}, "
                f"{conv_contract_expr(e['index'])}))")
    if t == "UnaryOp" and e.get("op") == "-":
        return f"(CNeg {conv_contract_expr(e['operand'])})"
    if t == "UnaryOp" and e.get("op") == "not":
        return f"(CNot {conv_contract_expr(e['operand'])})"
    if t == "Old":
        return f"(COld {conv_contract_expr(e['expr'])})"
    if t == "BinOp":
        op = e.get("op")
        if op in BINOP_MAP:
            return (f"(CBinOp ({BINOP_MAP[op]}, "
                    f"{conv_contract_expr(e['left'])}, "
                    f"{conv_contract_expr(e['right'])}))")
        if op in CONTRACT_CMP_MAP:
            return (f"({CONTRACT_CMP_MAP[op]} ("
                    f"{conv_contract_expr(e['left'])}, "
                    f"{conv_contract_expr(e['right'])}))")
        if op in CONTRACT_LOGIC_MAP:
            return (f"({CONTRACT_LOGIC_MAP[op]} ("
                    f"{conv_contract_expr(e['left'])}, "
                    f"{conv_contract_expr(e['right'])}))")
        raise NotInSimpleSubset(
            f"contract BinOp '{op}' not in subset")
    if t == "Boolean" or t == "Bool":
        return f"(CBoolLit {str(e.get('value', False)).lower()})"
    if t == "String":
        return f"(CStringLit {ocaml_char_list(e.get('value', ''))})"
    # Ghost array atoms
    if t == "GhostCopy":
        return f"(CGCopy {ocaml_char_list(e['arr'])})"
    if t == "GhostMake":
        return (f"(CGMake ({conv_contract_expr(e['size'])}, "
                f"{conv_contract_expr(e['default'])}))")
    if t == "GhostCopyRange":
        return (f"(CGCopyRange ({ocaml_char_list(e['arr'])}, "
                f"{conv_contract_expr(e['lo'])}, "
                f"{conv_contract_expr(e['hi'])}))")
    # Ghost tuple atoms
    if t == "MkTuple":
        elts = e.get("elts", [])
        if len(elts) == 2:
            return (f"(CGMkTuple2 ({conv_contract_expr(elts[0])}, "
                    f"{conv_contract_expr(elts[1])}))")
        if len(elts) == 3:
            return (f"(CGMkTuple3 ({conv_contract_expr(elts[0])}, "
                    f"{conv_contract_expr(elts[1])}, "
                    f"{conv_contract_expr(elts[2])}))")
        if len(elts) == 4:
            return (f"(CGMkTuple4 ({conv_contract_expr(elts[0])}, "
                    f"{conv_contract_expr(elts[1])}, "
                    f"{conv_contract_expr(elts[2])}, "
                    f"{conv_contract_expr(elts[3])}))")
        raise NotInSimpleSubset(
            f"MkTuple arity {len(elts)} not in subset (only 2/3/4)")
    if t == "FstExpr":
        return f"(CGFst {conv_contract_expr(e['tuple'])})"
    if t == "SndExpr":
        return f"(CGSnd {conv_contract_expr(e['tuple'])})"
    # Ghost list atoms
    if t == "GhostNil" or t == "Nil":
        return "CGNil"
    if t == "GhostCons":
        return (f"(CGCons ({conv_contract_expr(e['head'])}, "
                f"{conv_contract_expr(e['tail'])}))")
    # Ghost set atoms
    if t == "GhostSetEmpty" or t == "SetEmpty":
        return "CGSetEmpty"
    if t == "GhostSetAdd":
        return (f"(CGSetAdd ({conv_contract_expr(e['elem'])}, "
                f"{conv_contract_expr(e['set'])}))")
    if t == "GhostSetMem":
        return (f"(CGSetMem ({conv_contract_expr(e['elem'])}, "
                f"{conv_contract_expr(e['set'])}))")
    if t == "GhostSetCard":
        return f"(CGSetCard {conv_contract_expr(e['set'])})"
    # Ghost map/dict atoms
    if t == "MapEmpty" or t == "GhostMapEmpty":
        return "CGMapEmpty"
    if t == "GhostMapGet" or t == "MapGet":
        return (f"(CGMapGet ({conv_contract_expr(e['map'])}, "
                f"{conv_contract_expr(e['key'])}))")
    if t == "GhostMapSet" or t == "MapSet":
        return (f"(CGMapSet ({conv_contract_expr(e['map'])}, "
                f"{conv_contract_expr(e['key'])}, "
                f"{conv_contract_expr(e['value'])}))")
    if t == "GhostHasKey" or t == "HasKey":
        return (f"(CGHasKey ({conv_contract_expr(e['map'])}, "
                f"{conv_contract_expr(e['key'])}))")
    # Ghost list atoms (more)
    if t == "GhostListLen":
        return f"(CGListLen {conv_contract_expr(e['list'])})"
    if t == "GhostNth":
        return (f"(CGNth ({conv_contract_expr(e['list'])}, "
                f"{conv_contract_expr(e['index'])}))")
    raise NotInSimpleSubset(
        f"contract expression type '{t}' not in subset")


# Ghost-type tracking: Module 5's IR has per-statement ghost_type but
# Module 6 dynamically promotes augassigns via _resolve_effective_ghost_type
# (look up the var's declared ghost type). We mirror that by tracking
# the type declared at the first GhostAssign(op="=") per target.
_GHOST_TYPE_TABLE: Dict[str, str] = {}


def reset_ghost_table() -> None:
    _GHOST_TYPE_TABLE.clear()


def conv_stmt(s: Dict[str, Any]) -> str:
    """IR statement → OCaml expression of type `whyml_stmt`.
    Tuple-arg form for extracted constructors. """
    t = s.get("stmt")
    if t == "Pass":
        return "WSkip"
    if t == "Assign":
        return (f"(WAssign ({ocaml_ident(s['target'])}, "
                f"{conv_expr(s['value'])}))")
    if t == "AugAssign":
        op = s.get("op")
        if op not in AUG_OP_MAP:
            raise NotInSimpleSubset(
                f"AugAssign op '{op}' not in simple subset")
        return (f"(WAugAssign ({ocaml_ident(s['target'])}, "
                f"{AUG_OP_MAP[op]}, {conv_expr(s['value'])}))")
    if t == "ArraySet":
        arr = s["array"]
        if arr.get("type") != "Var":
            raise NotInSimpleSubset(
                "ArraySet array must be a Var (formal WArraySet takes "
                "an ident)")
        return (f"(WArraySet ({ocaml_char_list(arr['name'])}, "
                f"{conv_expr(s['index'])}, {conv_expr(s['value'])}))")
    if t == "Return":
        raise NotInSimpleSubset(
            "Return at any nesting (formal model uses WSeq+WAssign+"
            "WRaise pattern that diverges from Module 6's body-level "
            "emission — use bytediff_drop_trailing_return)")
    if t == "While":
        # WWhile now takes list contract_expr for invs/vars (added
        # 2026-05-28). Emit one element per source invariant/variant
        # to match Module 6's per-line emission.
        invariants = s.get("invariants", [])
        variants = s.get("variants", [])
        inv_list_ml = ("[" + "; ".join(conv_contract_expr(i)
                                       for i in invariants) + "]")
        var_list_ml = ("[" + "; ".join(conv_contract_expr(v)
                                       for v in variants) + "]")
        body_stmts = drop_trailing_return(s.get("body", []))
        if not body_stmts:
            body_stmts = [{"stmt": "Pass"}]
        return (f"(WWhile ({inv_list_ml}, {var_list_ml}, "
                f"{conv_expr(s['test'])}, {conv_seq(body_stmts)}))")
    if t == "Label":
        return f"(WLabel {ocaml_char_list(s['name'])})"
    if t == "Break":
        return "(WRaise ExcBreak)"
    if t == "Continue":
        return "(WRaise ExcContinue)"
    if t == "Raise":
        exc = s.get("exc_type", "PyCSL_Exception")
        return f"(WRaise (ExcNamed {ocaml_char_list(exc)}))"
    if t == "Assert":
        # Module 6 erases Python `assert` statements to `()`
        # (statements.py:1093-1096). The formal WAssert is reserved for
        # spec-level assertions (critical-section prove_invariant); map
        # Python `assert` to WSkip to match Module 6's erasure.
        return "WSkip"
    if t == "GhostAssign":
        target = s["target"]
        raw_gtype = s.get("ghost_type", "int")
        # Resolve effective ghost type per Module 6's
        # _resolve_effective_ghost_type semantics: for augassigns,
        # look up the target's previously-declared type.
        op = s.get("op", "=")
        if op == "=":
            if target in _GHOST_TYPE_TABLE:
                raise NotInSimpleSubset(
                    f"GhostAssign reassign with op='=' on existing var "
                    f"'{target}' (formal model has WGhostDecl and "
                    f"augassign WGhostAssign but no plain-set form; "
                    f"Module 6 emits `ghost x := val`)")
            gtype_str = raw_gtype
            _GHOST_TYPE_TABLE[target] = gtype_str
        else:
            gtype_str = _GHOST_TYPE_TABLE.get(target, raw_gtype)
        if gtype_str not in GHOST_TYPE_MAP:
            raise NotInSimpleSubset(
                f"GhostAssign type '{gtype_str}' not in subset")
        # op="=" → either first-time declaration (WGhostDecl) or
        # reassignment (WGhostAssign with synthetic AugAdd of e to 0?).
        # The formal model has WGhostDecl for first-time and WGhostAssign
        # for subsequent. Our converter can't easily track "first time"
        # globally so we use IR's `op` field: op="=" → WGhostDecl,
        # op in {+=, -=, *=} → WGhostAssign.
        gtype_ocaml = GHOST_TYPE_MAP[gtype_str]
        val_ocaml = conv_contract_expr(s["value"])
        if op == "=":
            return (f"(WGhostDecl ({ocaml_char_list(target)}, "
                    f"{gtype_ocaml}, {val_ocaml}))")
        if op in GHOST_AUG_OP_MAP:
            return (f"(WGhostAssign ({ocaml_char_list(target)}, "
                    f"{gtype_ocaml}, {GHOST_AUG_OP_MAP[op]}, "
                    f"{val_ocaml}))")
        raise NotInSimpleSubset(
            f"GhostAssign op '{op}' not in subset")
    if t == "CriticalSection":
        # Module 6 wraps the body with `assume { inv }` ; body ; `assert { inv }`
        # when the source `#@ critical lock` directive provides invariants.
        # Without invariants Module 6 just inlines the body (gen is transparent).
        raw_body = s.get("body", [])
        if raw_body and raw_body[-1].get("stmt") == "Return":
            raise NotInSimpleSubset(
                "CriticalSection body ending with Return — Module 6 "
                "emits the bare return value; formal model has no "
                "equivalent bare-value statement.")
        body_stmts = drop_trailing_return(raw_body)
        body_ws = conv_seq(body_stmts) if body_stmts else "WSkip"
        assume_inv = s.get("assume_invariant")
        prove_inv = s.get("prove_invariant")
        # Build the sequence (assume; body; assert) skipping missing parts.
        # The formal model treats CriticalSection's mutex as transparent
        # (concurrency is out of scope for Hoare WP); only the spec-level
        # wrappers are visible at this layer.
        if assume_inv is not None:
            assume_ws = (f"(WAssume {conv_contract_expr(assume_inv)})")
            body_ws = f"(WSeq ({assume_ws}, {body_ws}))"
        if prove_inv is not None:
            assert_ws = (f"(WAssert ({conv_contract_expr(prove_inv)}, "
                         f"{ocaml_char_list('')}))")
            body_ws = f"(WSeq ({body_ws}, {assert_ws}))"
        return body_ws
    if t == "Try":
        body_stmts = drop_trailing_return(s.get("body", []))
        handlers = s.get("handlers", [])
        if len(handlers) != 1:
            raise NotInSimpleSubset(
                f"Try with {len(handlers)} handlers (only single-handler "
                f"supported)")
        h = handlers[0]
        h_body = drop_trailing_return(h.get("body", []))
        exc_name = h.get("exc_type", "PyCSL_Exception")
        if "|" in exc_name:
            raise NotInSimpleSubset("Try handler with multiple exc types")
        if not body_stmts:
            body_stmts = [{"stmt": "Pass"}]
        if not h_body:
            h_body = [{"stmt": "Pass"}]
        return (f"(WTryCatch ({conv_seq(body_stmts)}, "
                f"{ocaml_char_list(exc_name.strip())}, "
                f"{conv_seq(h_body)}))")
    if t == "If":
        body_stmts = s.get("body", [])
        orelse_stmts = s.get("orelse", [])
        # If's body/orelse with Return triggers Module 6's "bare value
        # as last expression" emission (the no-early-return convention),
        # which the formal model doesn't reproduce (gen maps Return to
        # WSeq+WAssign+WRaise). Reject those.
        if body_stmts and body_stmts[-1].get("stmt") == "Return":
            raise NotInSimpleSubset(
                "If body ends with Return — Module 6 emits the bare "
                "return value at function level; formal model's "
                "WSeq+WAssign+WRaise pattern diverges")
        if orelse_stmts and orelse_stmts[-1].get("stmt") == "Return":
            raise NotInSimpleSubset(
                "If orelse ends with Return — same divergence")
        body_stmts = drop_trailing_return(body_stmts)
        orelse_stmts = drop_trailing_return(orelse_stmts)
        if not body_stmts:
            body_stmts = [{"stmt": "Pass"}]
        if not orelse_stmts:
            orelse_stmts = [{"stmt": "Pass"}]
        return (f"(WIf ({conv_expr(s['test'])}, "
                f"{conv_seq(body_stmts)}, {conv_seq(orelse_stmts)}))")
    raise NotInSimpleSubset(f"stmt type '{t}' not in simple subset")


def conv_seq(stmts: List[Dict[str, Any]]) -> str:
    """List of IR statements → right-leaning WSeq chain. Empty → WSkip."""
    if not stmts:
        return "WSkip"
    if len(stmts) == 1:
        return conv_stmt(stmts[0])
    head = conv_stmt(stmts[0])
    tail = conv_seq(stmts[1:])
    return f"(WSeq ({head}, {tail}))"


def drop_trailing_return(stmts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Drop the trailing Return so byte-diff focuses on body shape."""
    if stmts and stmts[-1].get("stmt") == "Return":
        return stmts[:-1]
    return stmts


# --------------------------------------------------------------------
# State extraction
# --------------------------------------------------------------------

def collect_assigned_locals(stmts: List[Dict[str, Any]]) -> List[str]:
    """Variables that get assigned in the body (Module 6 treats these as
    declared_refs after their first assignment).
    """
    out: List[str] = []
    seen: set[str] = set()
    for s in stmts:
        t = s.get("stmt")
        if t == "Assign" and s.get("target"):
            if s["target"] not in seen:
                out.append(s["target"])
                seen.add(s["target"])
    return out


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def run_module5(source_path: str) -> str:
    """Invoke pycsl-ir-dump.py via the project venv."""
    venv_py = ROOT / ".venv" / "bin" / "python"
    cmd = [str(venv_py), str(ROOT / "bin" / "pycsl-ir-dump.py"),
           source_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        sys.exit(2)
    return res.stdout


DRIVER_TEMPLATE = r'''
open EmitExtract

let to_char_list (s : string) : char list =
  let rec aux i acc =
    if i < 0 then acc else aux (i - 1) (s.[i] :: acc)
  in
  aux (String.length s - 1) []

let of_char_list (cs : char list) : string =
  let buf = Buffer.create 64 in
  List.iter (Buffer.add_char buf) cs;
  Buffer.contents buf

let json_str (s : string) : string =
  let buf = Buffer.create (String.length s + 2) in
  Buffer.add_char buf '"';
  String.iter (fun c -> match c with
    | '"'  -> Buffer.add_string buf "\\\""
    | '\\' -> Buffer.add_string buf "\\\\"
    | '\n' -> Buffer.add_string buf "\\n"
    | '\t' -> Buffer.add_string buf "\\t"
    | c when Char.code c < 0x20 ->
        Buffer.add_string buf (Printf.sprintf "\\u%04x" (Char.code c))
    | c -> Buffer.add_char buf c) s;
  Buffer.add_char buf '"';
  Buffer.contents buf

let aware_state_for () : aware_state =
  { aw_shared_vars   = [];
    aw_declared_refs = __DECLARED__;
    aw_local_refs    = __DECLARED__;
    aw_array_locals  = [];
    aw_bounded_int   = None }

let () =
  let ws : whyml_stmt = __ROCQ_AST__ in
  let out = emit_stmt_state_aware (aware_state_for ()) ws in
  Printf.printf "__CASE_ID__\t%s\n" (json_str (of_char_list out))
'''


def render_driver(rocq_ast: str, declared: list[str], case_id: str) -> str:
    decl_ml = "[" + "; ".join(f'(to_char_list "{d}")' for d in declared) + "]"
    return (DRIVER_TEMPLATE
            .replace("__ROCQ_AST__", rocq_ast)
            .replace("__DECLARED__", decl_ml)
            .replace("__CASE_ID__", case_id))


def main() -> None:
    args = sys.argv[1:]
    write_driver = None
    if "--driver" in args:
        i = args.index("--driver")
        write_driver = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print("usage: ir-to-rocq-ast.py <source.py> [--driver <output.ml>]",
              file=sys.stderr)
        sys.exit(2)
    src_path = args[0]
    ir = json.loads(run_module5(src_path))
    funcs = ir.get("functions", [])
    if not funcs:
        sys.stderr.write("[error] no functions in IR\n")
        sys.exit(2)
    fn = funcs[0]
    body = drop_trailing_return(fn.get("body", []))
    if not body:
        sys.stderr.write(
            f"[skip] {src_path}: body empty after dropping trailing Return "
            f"(nothing to byte-diff — formal and Module 6 differ on the "
            f"empty-body convention)\n")
        sys.exit(2)
    reset_ghost_table()
    try:
        ws = conv_seq(body)
    except NotInSimpleSubset as exc:
        sys.stderr.write(f"[skip] {src_path}: {exc}\n")
        sys.exit(2)
    decl = collect_assigned_locals(body)
    case_id = Path(src_path).stem
    out = {
        "function": fn["name"],
        "params": fn.get("formal_params", []),
        "declared": decl,
        "rocq_ast": ws,
        "case_id": case_id,
    }
    if write_driver:
        driver_src = render_driver(ws, decl, case_id)
        Path(write_driver).write_text(driver_src)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
